import os, sqlite3, random
from functools import wraps
from flask import Flask, g, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

# --- App setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
app.config['DATABASE'] = os.path.join(app.root_path, 'blackjack.sqlite3')

# --- DB helpers (Flaskr-style)
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with open(os.path.join(app.root_path, 'schema.sql'), 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    db.commit()

@app.route('/init-db')
def init_db_route():
    init_db()
    flash('Database initialized.')
    return redirect(url_for('index'))

# --- Auth utilities ---
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.')
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped

# --- Cards / Blackjack logic
RANKS = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
SUITS = ['♠','♥','♦','♣']  # unicode suits

def build_deck():
    return [f'{r}{s}' for s in SUITS for r in RANKS]

def card_value(card):
    r = card[:-1] if card[:-1] != '' else card  # handle '10'
    if r in ('J','Q','K'): return 10
    if r == 'A': return 11  # count aces as 11 first
    return int(r)

def hand_value(cards):
    total = sum(card_value(c) for c in cards)
    # adjust aces (treat as 1) while busting
    aces = sum(1 for c in cards if c[:-1] == 'A')
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def deal_one(deck):
    return deck.pop()

def game_over_state(player_cards, dealer_cards):
    ps = hand_value(player_cards)
    ds = hand_value(dealer_cards)
    if ps > 21: return 'L', ps, ds           # player bust
    if ds > 21: return 'W', ps, ds           # dealer bust
    if ps > ds: return 'W', ps, ds
    if ps < ds: return 'L', ps, ds
    return 'T', ps, ds

def persist_result(user_id, ps, ds, result):
    db = get_db()
    db.execute(
        'INSERT INTO games (user_id, player_score, dealer_score, result) VALUES (?, ?, ?, ?)',
        (user_id, ps, ds, result)
    )
    db.commit()

# --- Routes
@app.route('/')
def index():
    stats = None
    if 'user_id' in session:
        db = get_db()
        stats = db.execute("""
            SELECT
                SUM(CASE WHEN result='W' THEN 1 ELSE 0 END) AS wins,
                SUM(CASE WHEN result='T' THEN 1 ELSE 0 END) AS ties,
                SUM(CASE WHEN result='L' THEN 1 ELSE 0 END) AS losses
            FROM games WHERE user_id=?
        """, (session['user_id'],)).fetchone()
    return render_template('index.html', stats=stats)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']
        if not username or not password:
            flash('Username and password required.')
            return redirect(url_for('register'))
        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                       (username, generate_password_hash(password)))
            db.commit()
            flash('Registered! You can log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already taken.')
    return render_template('auth/register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']
        user = get_db().execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Welcome back!')
            return redirect(url_for('index'))
        flash('Invalid credentials.')
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.')
    return redirect(url_for('index'))

# --- Game flow ---
@app.route('/start')
@login_required
def start():
    deck = build_deck()
    random.shuffle(deck)
    player = [deal_one(deck), deal_one(deck)]
    dealer = [deal_one(deck), deal_one(deck)]
    session['deck'] = deck
    session['player'] = player
    session['dealer'] = dealer
    session['game_over'] = False
    return redirect(url_for('play'))

@app.route('/play')
@login_required
def play():
    deck = session.get('deck')
    player = session.get('player', [])
    dealer = session.get('dealer', [])
    game_over = session.get('game_over', False)

    player_score = hand_value(player) if player else 0
    dealer_score = hand_value(dealer) if dealer else 0

    # hide dealer's second card until game is over
    show_dealer_all = game_over
    return render_template('game/play.html',
                           player=player, dealer=dealer,
                           player_score=player_score,
                           dealer_score=dealer_score,
                           show_dealer_all=show_dealer_all,
                           game_over=game_over)

@app.post('/hit')
@login_required
def hit():
    deck = session['deck']
    player = session['player']
    player.append(deal_one(deck))
    session['deck'] = deck
    session['player'] = player

    # if player busts, end gam
    ps = hand_value(player)
    if ps > 21:
        dealer = session['dealer']
        result, ps, ds = 'L', ps, hand_value(dealer)
        persist_result(session['user_id'], ps, ds, result)
        session['game_over'] = True
    return redirect(url_for('play'))

@app.post('/stand')
@login_required
def stand():
    deck = session['deck']
    dealer = session['dealer']
    player = session['player']

    # dealer plays: hit until >=17
    while hand_value(dealer) < 17 and deck:
        dealer.append(deal_one(deck))

    session['dealer'] = dealer
    result, ps, ds = game_over_state(player, dealer)
    persist_result(session['user_id'], ps, ds, result)
    session['game_over'] = True
    return redirect(url_for('play'))

# --- Leaderboard & Cards page
@app.route('/leaderboard')
def leaderboard():
    db = get_db()
    rows = db.execute("""
      SELECT u.username,
             SUM(CASE WHEN g.result='W' THEN 1 ELSE 0 END) AS wins,
             SUM(CASE WHEN g.result='T' THEN 1 ELSE 0 END) AS ties,
             SUM(CASE WHEN g.result='L' THEN 1 ELSE 0 END) AS losses
      FROM users u
      LEFT JOIN games g ON u.id = g.user_id
      GROUP BY u.id, u.username
      ORDER BY wins DESC, ties DESC
      LIMIT 20
    """).fetchall()
    return render_template('leaderboard.html', rows=rows)

@app.route('/cards')
def cards():
    # renders all cards
    deck = build_deck()
    return render_template('cards.html', deck=deck)

# Static
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5051, debug=True, use_reloader=False)

