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

    @app.route('/sessions', methods=['GET', 'POST'])
    def sessions():
        if request.method == 'POST' or request.method == 'GET':
        # List all the students in the database
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE role = 'student';")
                    students = cur.fetchall()
                    # List course name from the database
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("SELECT course_name, course_id FROM courses;")
                    course_name = cur.fetchall()
                    cur.execute("SELECT course_id FROM courses;")
                    course_id = cur.fetchall()

            # List course ID from the database
            sessions = {}
            course_ids = []

            for it in course_id:
                with db.get_db() as con:
                    with con.cursor() as cur:
                        cur.execute("SELECT * FROM course_sessions where course_id = %s;", (it))
                        course_list = cur.fetchall()
                        tostring = str(it)
                        oneout = tostring.replace('[', '')
                        twoout= oneout.replace(']', '')
                        course_ids.append(twoout)
                        sessions.update( {twoout : course_list})


                        # List sessions in the database
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("SELECT * FROM course_sessions;")

        if request.method == 'POST':
            # Info from form field
            courses_name = request.form['courses_name']
            course_session_number = request.form['course_session_number']
            course_session_id = request.form.get('course_session_id', type=int)
            session_time = request.form['session_time']
            number_students = request.form['number_students']
            # Executions and Fetch for course_session_cursor
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("SELECT * FROM courses WHERE course_name = %s ;", (courses_name,))
                    cour = cur.fetchone()

            # Insert session info into database
            try:
                with db.get_db() as con:
                    with con.cursor() as cur:
                        cur.execute("INSERT INTO course_sessions (number, course_id, number_students, time) VALUES (%s,%s,%s,%s);", (course_session_number, cour[0], number_students, session_time))
                        con.commit()
                        flash("Your session was added. You may now add students to this session using the directory.")
            except:
                flash("We could not add this session. Check the name and try again.")
            return render_template('sessions.html', course_session_id=course_session_id, session_time=session_time, courses_name=courses_name, course_session_number=course_session_number, cour=cour, number_students=number_students,students=students, course_list=course_list, course_name=course_name, sessions=sessions, course_ids=course_ids)


    from . import courses
    app.register_blueprint(courses.bp)

    from . import auth
    app.register_blueprint(auth.bp)


    return app
