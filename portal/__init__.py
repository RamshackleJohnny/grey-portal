from flask import Flask, render_template, request

import psycopg2

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

    @app.route('/', methods=['GET', 'POST'])
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            error = None
            print('Lets get it started!')
            email = request.form['email']
            password = request.form['password']
            print(email)
            print(password)
            connection = psycopg2.connect(database = "portal")
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email,password)) 
            userdata = cursor.fetchone()
            wrong = 'username or password is incorrect'
            if userdata == None:
                return render_template('index.html', wrong=wrong)
            print(userdata)

            
        return render_template('login.html')

    return app
