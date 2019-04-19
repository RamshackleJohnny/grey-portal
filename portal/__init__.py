import functools

from flask import Flask, render_template, request, session, redirect, url_for, g, flash

import psycopg2
import psycopg2.extras
from psycopg2.extras import DictCursor

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

    def login_required(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                return redirect(url_for('index'))

            return view(**kwargs)

        return wrapped_view

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
        if request.method == 'GET':
            # List all the students in the database
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE role = 'student';")
                    students = cur.fetchall()

            # List all courses in the database
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("SELECT course_name FROM courses;")
                    course_list = cur.fetchall()
                    print(course_list)

            # List sessions in the database
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("SELECT * FROM course_sessions;")
                    session_list = cur.fetchall()
                    print(session_list)

            # List user sessions in the database
            # with db.get_db() as con:
            #    with con.cursor() as cur:
            # cur.execute("SELECT * FROM user_sessions;")
            # user_sessions = cur.fetchall()
            # REMEMBER TO PUT user_sessions IN render_template AFTER UNCOMMENTING


            return render_template('sessions.html', students=students, course_list=course_list, session_list=session_list)

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
                    print(cour[0])

            # Insert session info into database
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("INSERT INTO course_sessions (number, course_id, number_students, time) VALUES (%s,%s,%s,%s);", (course_session_number, cour[0], number_students, session_time))
                    con.commit()

            return render_template('sessions.html', course_session_id=course_session_id, session_time=session_time, courses_name=courses_name, course_session_number=course_session_number, cour=cour, number_students=number_students)
        return render_template('sessions.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            error = None
            print('Lets get it started!')
            email = request.form['email']
            password = request.form['password']
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email,password,))
                    userdata = cur.fetchone()
            wrong = 'Username or password is incorrect'
            if userdata == None:
                return render_template('index.html', wrong=wrong)
            else:
                dict_cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
                dict_cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email,password,))
                sesh = dict_cur.fetchone()
                session.clear()
                session['user_id'] = sesh['id']
                return redirect(url_for('dash'))
        return render_template('index.html')

    @app.route('/courses', methods=['GET', 'POST'])
    @login_required
    def course_page():
        # Lets grab the users role via session ID here.
        with db.get_db() as con:
            with con.cursor() as cur:
                user_id= g.user[0]
                cur.execute("SELECT role, id FROM users WHERE id = %s", [user_id])
                users_role = cur.fetchone()
        print(f"users_role: {users_role}")
        if request.method== 'POST':
            print("Let's do this again.")
            course_name=request.form['coursename']
            course_desc=request.form['coursedesc']
            course_num=request.form['coursenumber']
            try:
                with db.get_db() as con:
                    with con.cursor() as cur:
                        cur.execute("INSERT INTO courses (course_name, description, course_number, teacher_id) VALUES (%s, %s, %s, %s)", (course_name, course_desc, course_num, g.user[0]))
                        con.commit()
                flash(f"Your course, \"{course_name}\", was added with you as the teacher. You may now add students to this course and add sessions.")
            except Exception as e:
                flash("We could not add this course. A course with that name may already exist.")
                print(e)
            finally:
                with db.get_db() as con:
                    with con.cursor() as cur:
                        cur.execute("SELECT course_name, description, teacher_id, course_id FROM courses ORDER BY course_name ASC")
                        all_courses= cur.fetchall()
                        cur.execute("SELECT first_name, last_name, id FROM users WHERE role='teacher'")
                        all_teachers = cur.fetchall()
                return render_template('courses.html', all_courses=all_courses, all_teachers=all_teachers, users_role=users_role)
        else:
            # THIS IS GET
            # Ugh. -Danny.
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("SELECT course_name, description, teacher_id, course_id FROM courses ORDER BY course_name ASC")
                    all_courses = cur.fetchall()
                    cur.execute("SELECT first_name, last_name, id  FROM users WHERE role='teacher'")
                    all_teachers = cur.fetchall()
            return render_template('courses.html', all_courses=all_courses, all_teachers=all_teachers, users_role=users_role)

    def get_course(id):
        with db.get_db() as con:
            with con.cursor() as cur:
                cur.execute('SELECT course_id, course_name, description, course_number FROM courses WHERE course_id= %s', [id])
                course = cur.fetchone()
        return course

    @app.route('/<id>/course-delete', methods=('POST','GET'))
    def delete_course(id):
        get_course(id)
        with db.get_db() as con:
            with con.cursor() as cur:
                cur.execute('DELETE FROM courses WHERE course_id= %s',[id])
                con.commit()
        return redirect(url_for('course_page'))

    @app.route('/<id>/course-update', methods=['GET', 'POST'])
    def update_course(id):
        course = get_course(id)
        if request.method== 'POST':
            new_name= request.form['course-name']
            new_desc= request.form['course-desc']
            new_num= request.form['course-num']
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("UPDATE courses SET course_name=%s, description=%s, course_number=%s WHERE course_id= %s", [new_name, new_desc, new_num, id])
                    con.commit()
            return redirect(url_for('course_page'))
        return render_template('update-course.html', course=course)

    @app.route('/assignments', methods=['GET', 'POST'])
    def assignment_page():
        return render_template('assignments.html')


    @app.route('/logout')
    def log_out():
        session.clear()
        return redirect(url_for('index'))

    return app
