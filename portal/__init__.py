from flask import Flask, render_template, request, session, redirect, url_for, g

import psycopg2
import psycopg2.extras

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DB_NAME='portal',
        DB_USER='portal_user',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    from . import db
    db.init_app(app)

    @app.before_request
    def before_request():
        user_id = session.get('user_id')

        print(request.endpoint)
        if request.endpoint != 'index' and request.endpoint != 'login':
            if user_id is None:
                return redirect(url_for('index'))
            else:
                print('User is authorized')
        else:
            print('And they are not on index or login')


    @app.route('/', methods=['GET', 'POST'])
    def index():
        session.clear()
        return render_template('index.html')

    @app.route('/dashboard', methods=['GET', 'POST'])
    def dash():
        return render_template('dash.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        session.clear()
        if request.method == 'POST':
            error = None
            print('Lets get it started!')
            email = request.form['email']
            password = request.form['password']
            log = db.get_db()
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


    return app
