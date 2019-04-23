import functools

from flask import Flask, render_template, request, session, redirect, url_for, g, flash, abort

import psycopg2
import psycopg2.extras

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

    @app.route('/create-course', methods=['GET', 'POST'])
    @login_required
    def create_course():
        if not g.user[5]=='teacher':
           return abort(403)
        course_name=request.form['coursename']
        course_desc=request.form['coursedesc']
        course_num=request.form['coursenumber']
        connection = db.get_db()
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO courses (course_name, description, course_number, teacher_id) VALUES (%s, %s, %s, %s)", (course_name, course_desc, course_num, g.user[0]))
            connection.commit()
            flash(f"Your course, \"{course_name}\", was added with you as the teacher. You may now add students to this course and add sessions.")
        except psycopg2.errors.UniqueViolation:
            flash(f"Your course already exists with that code or with that course name. Please check the directory.")
        except psycopg2.errors.NotNullViolation:
            flash(f"Not all required information was submitted. Please fill in the form again.")
        finally:
            return redirect(url_for('course_page'))


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
        # print(f"users_role: {users_role}")
        cursor.execute("SELECT course_name, description, teacher_id, course_id, course_number FROM courses ORDER BY course_name ASC")
        all_courses = cursor.fetchall()
        cursor.execute("SELECT first_name, last_name, id  FROM users WHERE role='teacher'")
        all_teachers = cursor.fetchall()
        return render_template('courses.html', all_courses=all_courses, all_teachers=all_teachers, users_role=users_role)

    def get_course(id):
        connection = db.get_db()
        cursor = connection.cursor()
        cursor.execute('SELECT course_id, course_name, description, course_number, teacher_id FROM courses WHERE course_id= %s', [id])
        course = cursor.fetchone()
        return course

    @app.route('/<id>/course-delete', methods=('POST','GET'))
    @login_required
    def delete_course(id):
        course = get_course(id)
        if not g.user[0] == course[4]:
           return abort(403)
        connection = db.get_db()
        cursor = connection.cursor()
        cursor.execute('SELECT course_name FROM courses WHERE course_id= %s',[id])
        selected_course = cursor.fetchone()
        cursor.execute('DELETE FROM courses WHERE course_id= %s',[id])
        connection.commit()
        flash(f"\"{selected_course[0]}\" has been deleted.")
        return redirect(url_for('course_page'))

    @app.route('/<id>/course-update', methods=['GET', 'POST'])
    @login_required
    def update_course(id):
        course = get_course(id)
        if course is None:
            print(f"User {g.user[0]} is attempting to edit a course that doesn't exist.")
            return abort(404)
        if course[4] is not g.user[0]:
            print(f"User {g.user[0]} is attempting to edit a course that doesn't belong to them.")
            return abort(403)
        if request.method== 'POST':
            new_name= request.form['course-name']
            new_desc= request.form['course-desc']
            new_num= request.form['course-num']
            connection = db.get_db()
            cursor = connection.cursor()
            cursor.execute("UPDATE courses SET course_name=%s, description=%s, course_number=%s WHERE course_id= %s", [new_name, new_desc, new_num, id])
            connection.commit()
            flash(f"\"{new_name}\" has been updated.")
            return redirect(url_for('course_page'))
        return render_template('update-course.html', course=course)

    @app.route('/logout')
    def log_out():
        session.clear()
        return redirect(url_for('index'))

    return app
