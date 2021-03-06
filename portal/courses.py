from flask import Flask, render_template, request, session, redirect, url_for, g, flash, abort, Blueprint

from .db import get_db
from .auth import login_required, teacher_required

bp = Blueprint('courses', __name__)

@bp.route("/testing")
def test_page():
    return "Hello World."

@bp.route('/create-course', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_course():
    if not g.user[5]=='teacher':
       return abort(403)
    course_name=request.form['coursename']
    course_desc=request.form['coursedesc']
    course_num=request.form['coursenumber']
    connection = get_db()
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
        return redirect(url_for('courses.course_page'))


@bp.route('/courses', methods=['GET', 'POST'])
@login_required
def course_page():
    # Lets grab the users role via session ID here.
    connection = get_db()
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
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute('SELECT course_id, course_name, description, course_number, teacher_id FROM courses WHERE course_id= %s', [id])
    course = cursor.fetchone()
    return course

@bp.route('/<id>/course-delete', methods=('POST','GET'))
@login_required
@teacher_required
def delete_course(id):
    course = get_course(id)
    if not g.user[0] == course[4]:
       return abort(403)
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute('SELECT course_name FROM courses WHERE course_id= %s',[id])
    selected_course = cursor.fetchone()
    cursor.execute('DELETE FROM courses WHERE course_id= %s',[id])
    connection.commit()
    flash(f"\"{selected_course[0]}\" has been deleted.")
    return redirect(url_for('courses.course_page'))

@bp.route('/<id>/course-update', methods=['GET', 'POST'])
@login_required
@teacher_required
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
        connection = get_db()
        cursor = connection.cursor()
        cursor.execute("UPDATE courses SET course_name=%s, description=%s, course_number=%s WHERE course_id= %s", [new_name, new_desc, new_num, id])
        connection.commit()
        flash(f"\"{new_name}\" has been updated.")
        return redirect(url_for('courses.course_page'))
    return render_template('update-course.html', course=course)
