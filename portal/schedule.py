from flask import Flask, render_template, request, session, redirect, url_for, g, flash, abort, Blueprint

from .db import get_db
from .auth import login_required

bp = Blueprint('schedule', __name__)

@bp.route("/schedule", methods=['GET', 'POST'])
@login_required
def schedule():
    
    current_student = g.user[0]

    
    # List of schedule for student
    with get_db() as con:
        with con.cursor() as cur:
            cur.execute("SELECT session_id FROM user_sessions WHERE student_id = %s ORDER BY session_id ASC;", (current_student,))
            schedule_list = cur.fetchall()

    
    return render_template('schedule.html', schedule_list=schedule_list)
            