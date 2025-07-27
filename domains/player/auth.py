import functools
import sqlite3
from flask import (
    Blueprint, flash, redirect, render_template,
    request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from infrastructure.database.db import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.session.execute(
                    "INSERT INTO user (username, password) VALUES (:username, :password)",
                    {"username": username, "password": generate_password_hash(password)}
                )
                db.session.commit()
            except sqlite3.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for('auth.login'))

        flash(error)

    return render_template('player/auth/register.html')


@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        user = db.session.execute(
            "SELECT * FROM user WHERE username = :username",
            {"username": username}
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('core.index'))

        flash(error)

    return render_template('player/auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('core.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
