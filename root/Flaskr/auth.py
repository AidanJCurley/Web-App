import functools

from werkzeug.security import check_password_hash, generate_password_hash

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from root.Flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')
"""
Creates a blueprint named 'auth'. It is told that it is defined in __name__, and the url prefix will be prepended
to all URLs associated with the blueprint
"""


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """
    (1) --> @bp.route associates the URL /register with the register view func.
    (2) --> if the user submitted the form, request.method will be 'POST' - validate input
    (3) --> request.form is a special type of dict mapping submitted form keys and values. The user will input
            their username and password
    (4) --> validate username & password are not empty
    (5) --> validate username & password is not already registered by querying the database and checking if
            a result is returned.
            --> db.execute() takes a SQL Query with ? placeholders for any user input, and a tuple of values
                to replace the placeholders with. The database lib will take care of escaping values so we are
                not vulnerable to an SQL injection attack
    (6) --> if validation succeeds, insert new user database, using a password hash. db commit commits the changes
            to the data
    (7) --> url_for() generates the url and redirect() creates a redirect response to said url
    (8) --> flash() stores messages that can be retrieved when rendering the template
    :return:
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif(
            db.execute('SELECT id FROM user WHERE username = ?', (username,)).fetchone() is not None
        ):
            error = f'User {username} is already registered'

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            # uses cookies with session, a dict that stores user id data
            session['user_id'] = user['id']
            return redirect(url_for('index'))
    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))