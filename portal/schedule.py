from flask import Flask, render_template, request, session, redirect, url_for, g, flash, abort, Blueprint

from .db import get_db
from .auth import login_required, student_required

bp = Blueprint('schedule', __name__)

@bp.route("/schedule", methods=['GET', 'POST'])
@login_required
@student_required
def schedule():

    current_student = g.user[0]


    # List of schedule for student
    with get_db() as con:
        with con.cursor() as cur:
            cur.execute("SELECT course_name, time, description, session_id, teacher_id FROM user_sessions u_s JOIN course_sessions c_s ON c_s.id = u_s.session_id JOIN courses courses ON courses.course_id = c_s.course_id WHERE student_id = %s;", (current_student,))
            schedule_list = cur.fetchall()
            print(schedule_list)
        # Can I make it find the teacher too? We'll see!! -Danny
        connection = get_db()
        cursor = connection.cursor()
        cursor.execute("SELECT first_name, last_name, id  FROM users WHERE role='teacher'")
        all_teachers = cursor.fetchall()
    return render_template('schedule.html', schedule_list=schedule_list, all_teachers=all_teachers)
