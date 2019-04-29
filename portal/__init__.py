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


    @app.route('/assignments', methods=['GET', 'POST'])
    def assignment_page():
        with db.get_db() as con:
            with con.cursor() as cur:
                cur.execute("SELECT assignment_name, points_earned, points_available, instructions, completed FROM assignments ORDER BY assignment_name ASC")
                all_assignments = cur.fetchall()
                cur.execute("SELECT first_name, last_name, id FROM users WHERE role='teacher'")
                all_teachers = cur.fetchall()
        if request.method== 'POST':
            assign_name = request.form['assign-name']
            points_ttl = request.form['points-avb']
            instructions = request.form['instructions']
            session = request.form['session']
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("INSERT INTO assignments (assignment_name, points_available, instructions, completed, session_name) VALUES (%s,%s,%s,%s,%s);", (assign_name, points_ttl, instructions, False,session ))
                    con.commit()
            return redirect(url_for('assignment_page'))
        return render_template('assignments.html', all_assignments = all_assignments)

    def get_assignment(id):
        print('It gives me',id)
        with db.get_db() as con:
            with con.cursor() as cur:
                cur.execute('SELECT assignment_name FROM assignments WHERE assignment_id = %s', [id])
                assignment = cur.fetchone()
        return assignment

    @app.route('/<id>/assignment-delete', methods=('POST','GET'))
    def delete_assignment(id):
        get_assignment(id)
        with db.get_db() as con:
            with con.cursor() as cur:
                cur.execute('DELETE FROM assignments WHERE assignment_id = %s',[id])
                con.commit()
        return redirect(url_for('course_page'))

    return app
