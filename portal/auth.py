import functools

from flask import Flask, render_template, request, session, redirect, url_for, g, flash, abort, Blueprint
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
import psycopg2.extras

from portal.db import get_db

bp = Blueprint('auth', __name__)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('index'))

        return view(**kwargs)

    return wrapped_view


def student_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user['role']=='teacher':
            return abort(403)
        return view(**kwargs)

    return wrapped_view

def teacher_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user['role']=='student':
            return abort(403)


        return view(**kwargs)

    return wrapped_view


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        error = None
        print('Lets get it started!')
        email = request.form['email']
        password = request.form['password']
        log = get_db()
        cursor = log.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", [email])
        userdata = cursor.fetchone()
        print(userdata)
        if userdata == None:
            wrong = 'That user doesn\'t exist.'
            return render_template('index.html', wrong=wrong)
        elif not check_password_hash(userdata[4], password):
            wrong = 'Incorrect password.'
            return render_template('index.html', wrong=wrong)
        else:
            dict_cur = log.cursor(cursor_factory=psycopg2.extras.DictCursor)
            dict_cur.execute("SELECT * FROM users WHERE email = %s", [email])
            sesh = dict_cur.fetchone()
            session.clear()
            session['user_id'] = sesh['id']
            return redirect(url_for('dash'))
    return render_template('index.html')



@bp.route('/logout')
def log_out():
    session.clear()
    return redirect(url_for('index'))
