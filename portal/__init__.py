import functools

from flask import Flask, render_template, request, session, redirect, url_for, g, flash

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
            log = db.get_db()
            cursor = log.cursor()
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            g.user = cursor.fetchone()

    @app.route('/', methods=['GET', 'POST'])
    def index():
        return render_template('index.html')

    @app.route('/dashboard', methods=['GET', 'POST'])
    def dash():
        if request.method == 'GET':
            database = db.get_db()
            cursor = database.cursor()
            cursor.execute("SELECT * FROM users WHERE role = 'student';")
            students = cursor.fetchall()

            print(students)
            return render_template('dash.html', students=students)

        if request.method == 'POST':
            database = db.get_db()
            cursor = database.cursor()
            add_student = request.form['add_student']
            # remove_student = request.form['remove_student']
            cursor.execute("SELECT (id, email) FROM users WHERE role = 'student' AND email = %s;", (add_student,))
            # cursor.execute("SELECT (id, %s) FROM users WHERE role = 'student';", (remove_student))
            return render_template('dash.html', add_student=add_student)


        return render_template('dash.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
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

    @app.route('/courses', methods=['GET', 'POST'])
    @login_required
    def course_page():
        # Lets grab the users role via session ID here.
        connection = db.get_db()
        cursor = connection.cursor()
        # user_id = session.get('user_id')
        user_id= g.user[0]
        cursor.execute("SELECT role, id FROM users WHERE id = %s", [user_id])
        users_role = cursor.fetchone()
        print(f"users_role: {users_role}")
        if request.method== 'POST':
            print("Let's do this again.")
            course_name=request.form['coursename']
            course_desc=request.form['coursedesc']
            course_num=request.form['coursenumber']
            try:
                cursor.execute("INSERT INTO courses (course_name, description, course_number, teacher_id) VALUES (%s, %s, %s, %s)", (course_name, course_desc, course_num, g.user[0]))
                connection.commit()
                flash(f"Your course, \"{course_name}\", was added with you as the teacher. You may now add students to this course and add sessions.")
            except Exception as e:
                flash("We could not add this course. A course with that name may already exist.")
                print(e)
            finally:
                cursor.execute("SELECT course_name, description, teacher_id FROM courses ORDER BY course_name ASC")
                all_courses= cursor.fetchall()
                cursor.execute("SELECT first_name, last_name, id FROM users WHERE role='teacher'")
                all_teachers = cursor.fetchall()
                return render_template('courses.html', all_courses=all_courses, all_teachers=all_teachers, users_role=users_role)
        else:
            # THIS IS GET
            # Ugh. -Danny.
            cursor.execute("SELECT course_name, description, teacher_id FROM courses ORDER BY course_name ASC")
            all_courses = cursor.fetchall()
            cursor.execute("SELECT first_name, last_name, id  FROM users WHERE role='teacher'")
            all_teachers = cursor.fetchall()
            return render_template('courses.html', all_courses=all_courses, all_teachers=all_teachers, users_role=users_role)

    # def get_course(id):
	# 	cur.execute('SELECT course_name FROM courses WHERE course_name= %s', [course_name])
	# 	course = cur.fetchone()
	# 	return course
    # @app.route('courses/<int:id>/delete', methods=('POST','GET'))
	# def delete(id):
	# 	get_course(id)
	# 	cur.execute('DELETE FROM courses WHERE course_name= %s',[id])
	# 	conn.commit()
	# 	return redirect(url_for('index'))

    @app.route('/logout')
    def log_out():
        session.clear()
        return redirect(url_for('index'))

    return app
