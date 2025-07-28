from flask import Blueprint, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user
from domains.player.models import Player
from infrastructure.database.db import db
from domains.player.forms import RegistrationForm, LoginForm

auth_bp = Blueprint('player_auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if Player.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "error")
            return redirect(url_for('player_auth.login'))

        player = Player(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(player)
        db.session.commit()
        login_user(player)
        return redirect(url_for('core.index'))

    return render_template('player/auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        player = Player.query.filter_by(email=form.email.data).first()
        if player and player.check_password(form.password.data):
            login_user(player)
            return redirect(url_for('core.index'))
        flash("Invalid credentials.", "error")
    return render_template('player/auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('player_auth.login'))
