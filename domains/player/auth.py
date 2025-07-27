from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user
from domains.player.models import Player
from infrastructure.database.db import db

auth_bp = Blueprint('player_auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form['name']
        email    = request.form['email']
        password = request.form['password']

        existing = Player.query.filter_by(email=email).first()
        if existing:
            flash("Email already registered.", "error")
            return redirect(url_for('player_auth.login'))

        player = Player(name=name, email=email, password=password)
        db.session.add(player)
        db.session.commit()
        login_user(player)
        return redirect(url_for('core.index'))

    # notice the subpath:
    return render_template('player/auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']

        player = Player.query.filter_by(email=email).first()
        if player and player.password == password:
            login_user(player)
            return redirect(url_for('core.index'))

        flash("Invalid credentials.", "error")

    return render_template('player/auth/login.html')


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('player_auth.login'))
