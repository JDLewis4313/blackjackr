from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    # simple link to the game page
    return '<h1>Blackjackr (clean)</h1><p><a href="/game">Play the game</a></p>'

@app.route("/game")
def game():
    return render_template("game.html")

if __name__ == "__main__":
    app.run(debug=True)
