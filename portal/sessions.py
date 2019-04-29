import functools

from flask import Flask, render_template, request, session, redirect, url_for, g, flash, abort, Blueprint
import psycopg2
import psycopg2.extras

from portal.db import get_db

bp = Blueprint('sessions', __name__)

@bp.route('/sessions', methods=['GET', 'POST'])
def sessions():
    if request.method == 'POST' or request.method == 'GET':
    # List all the students in the database
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE role = 'student';")
                students = cur.fetchall()
                # List course name from the database
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("SELECT course_name, course_id FROM courses;")
                course_name = cur.fetchall()
                cur.execute("SELECT course_id FROM courses;")
                course_id = cur.fetchall()

        # List course ID from the database
        sessions = {}
        course_ids = []

        for it in course_id:
            with get_db() as con:
                with con.cursor() as cur:
                    cur.execute("SELECT * FROM course_sessions where course_id = %s;", (it))
                    course_list = cur.fetchall()
                    tostring = str(it)
                    oneout = tostring.replace('[', '')
                    twoout= oneout.replace(']', '')
                    course_ids.append(twoout)
                    sessions.update( {twoout : course_list})


                    # List sessions in the database
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("SELECT * FROM course_sessions;")
        return render_template('sessions.html', students=students, course_name=course_name, course_id = course_id, sessions=sessions)

    if request.method == 'POST':
        # Info from form field
        courses_name = request.form['courses_name']
        course_session_number = request.form['course_session_number']
        course_session_id = request.form.get('course_session_id', type=int)
        session_time = request.form['session_time']
        number_students = request.form['number_students']
        # Executions and Fetch for course_session_cursor
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("SELECT * FROM courses WHERE course_name = %s ;", (courses_name,))
                cour = cur.fetchone()

        # Insert session info into database
        try:
            with get_db() as con:
                with con.cursor() as cur:
                    cur.execute("INSERT INTO course_sessions (number, course_id, number_students, time) VALUES (%s,%s,%s,%s);", (course_session_number, cour[0], number_students, session_time))
                    con.commit()
                    flash("Your session was added. You may now add students to this session using the directory.")
        except:
            flash("We could not add this session. Check the name and try again.")
        return render_template('sessions.html', course_session_id=course_session_id, session_time=session_time, courses_name=courses_name, course_session_number=course_session_number, cour=cour, number_students=number_students,students=students, course_list=course_list, course_name=course_name, sessions=sessions, course_ids=course_ids)
