import functools

from flask import Flask, render_template, request, session, redirect, url_for, g, flash, abort, Blueprint
import psycopg2
import psycopg2.extras
from .auth import login_required, teacher_required

from portal.db import get_db

bp = Blueprint('sessions', __name__)

@bp.route('/sessions', methods=['GET', 'POST'])
@login_required
@teacher_required
def sessions():
    number_students=[]
    session_time = []
    course_session_id = []
    course_session_number = []
    courses_name = []
    cour = []
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

    if request.method == 'POST':
        # Info from form field
        courses_name = request.form['courses_name']
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
                    cur.execute("INSERT INTO course_sessions (course_id, number_students, time) VALUES (%s,%s,%s);", (cour[0], number_students, session_time))
                    con.commit()
                    flash("Your session was added. You may now add students to this session using the directory.")
        except:
            flash("We could not add this session. Check the name and try again.")
        return redirect(url_for('sessions.sessions'))
    return render_template('sessions.html',  course_session_id=course_session_id, session_time=session_time, courses_name=courses_name, cour=cour, number_students=number_students,students=students, course_name=course_name, sessions=sessions, course_ids=course_ids)

@bp.route('/update-session', methods=['GET', 'POST'])
@login_required
@teacher_required
def update_session():
    with get_db() as con:
        with con.cursor() as cur:
            cur.execute("SELECT id FROM course_sessions")
            sesh_ids = cur.fetchall()

    thepeople = {}
    sessions = {}
    session_ids = []
    for it in sesh_ids:
        with get_db() as con:
            with con.cursor() as cur:
                # join this table to users table to display specific user's info
                cur.execute("SELECT student_id FROM user_sessions WHERE session_id = %s;", (it))
                course_list = cur.fetchall()
                newest = []
                for item in course_list:
                    tostring = str(item)
                    oneout = tostring.replace('[', '')
                    twoout= oneout.replace(']', '')
                    newest.append(twoout)
        sessions[f'{it[0]}'] = newest
        #print(sessions)
        for names in course_list:
            with get_db() as con:
                with con.cursor() as cur:
                    cur.execute("SELECT first_name, last_name FROM users where id = %s;", (names))
                    namelist = cur.fetchall()
                    #print(namelist)
                    newestlist = []
                    for item in namelist:
                        print(item[1])
                        newestlist.extend(item)
                    thepeople[f'{names[0]}'] = newestlist




    # List all from users with the role 'student'
    with get_db() as con:
        with con.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE role = 'student';")
            students = cur.fetchall()

    # List all from course_sessions
    with get_db() as con:
        with con.cursor() as cur:
            cur.execute("SELECT * FROM course_sessions ORDER BY course_id ASC;")
            course_sessions = cur.fetchall()

    # List all from user_sessions
    with get_db() as con:
        with con.cursor() as cur:
            cur.execute("SELECT * FROM user_sessions;")
            user_sessions = cur.fetchall()

    # Join table for user_sessions and users
    with get_db() as con:
        with con.cursor() as cur:
            cur.execute("SELECT id, first_name, last_name FROM users users LEFT JOIN user_sessions us ON users.id = us.student_id ORDER BY id ASC;")
            students_in_sessions = cur.fetchall()
            #print(students_in_sessions)

    if request.method == 'POST':


        student_id = request.form['student_id']
        session_id = request.form['session_id']

        # before inserting these values, check that this pair of values ins't already in the user_sessions table
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("SELECT * FROM user_sessions WHERE student_id = %s AND session_id = %s;", (student_id, session_id))
                theyin = cur.fetchall()
                print(theyin)
            if theyin == []:
                with get_db() as con:
                    with con.cursor() as cur:
                        cur.execute("INSERT INTO user_sessions (student_id, session_id) VALUES (%s,%s); ", (student_id, session_id))
                        con.commit()
            else:
                flash(f"This student is already in this session.")



        return redirect(url_for('sessions.update_session'))

    return render_template('update-session.html',thepeople=thepeople, students=students, course_sessions=course_sessions, user_sessions=user_sessions, session_students=students_in_sessions,sessions=sessions, session_ids=session_ids)
