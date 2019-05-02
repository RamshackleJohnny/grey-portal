import functools

from flask import Flask, render_template, request, session, redirect, url_for, g, flash, abort

import psycopg2

def page_not_found(e):
	return render_template('404.html')

def server_error(e):
	return render_template('500.html')

def forbidden(e):
	return render_template('403.html')

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DB_NAME='portal',
        DB_USER='portal_user',
    )
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, server_error)
    app.register_error_handler(403, forbidden)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)


    from . import db
    db.init_app(app)

    @app.before_request
    def before_request():
        user_id = session.get('user_id')

        if user_id is None:
            g.user = None
        else:
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
                    g.user = cur.fetchone()

    @app.route('/', methods=['GET', 'POST'])
    def index():
        return render_template('index.html')

    @app.route('/dashboard', methods=['GET', 'POST'])
    def dash():

        return render_template('dash.html')

    from . import sessions
    app.register_blueprint(sessions.bp)

    from . import courses
    app.register_blueprint(courses.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import schedule
    app.register_blueprint(schedule.bp)

    from . import assign
    app.register_blueprint(assign.bp)

    return app
