import functools

from flask import Flask, render_template, request, session, redirect, url_for, g, flash, abort, Blueprint
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
            return redirect(url_for('dash'))
        return view(**kwargs)
      
    return wrapped_view
          
def teacher_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user['role']=='student':
            return redirect(url_for('dash'))


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
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email,password,))
        userdata = cursor.fetchone()
        wrong = 'Username or password is incorrect'
        if userdata == None:
            return render_template('index.html', wrong=wrong)
        else:
            dict_cur = log.cursor(cursor_factory=psycopg2.extras.DictCursor)
            dict_cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email,password,))
            sesh = dict_cur.fetchone()
            session.clear()
            session['user_id'] = sesh['id']
            return redirect(url_for('dash'))
    return render_template('index.html')



@bp.route('/logout')
def log_out():
    session.clear()
    return redirect(url_for('index'))
