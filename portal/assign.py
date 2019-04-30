from flask import Flask, render_template, request, session, redirect, url_for, g, flash, abort, Blueprint
import functools
from portal.db import get_db
import psycopg2
import psycopg2.extras

bp = Blueprint('assign', __name__)


@bp.route('/assignments', methods=['GET', 'POST'])
def assignment_page():
    student_assignments = []
    teach_assignments = []
    with get_db() as con:
        with con.cursor() as cur:
            this_teach = g.user[0]
            cur.execute("SELECT course_id, course_name FROM courses WHERE teacher_id = %s;", (this_teach,))
            thier_classes = cur.fetchall()
            cur.execute("SELECT student_id,session_id FROM user_sessions WHERE student_id = %s;", (this_teach,))
            students_classes = cur.fetchall()
            for tc in students_classes:
                with get_db() as con:
                    with con.cursor() as cur:
                        cur.execute("SELECT assignment_name, points_earned, points_available, instructions, sesh_id FROM assignments WHERE sesh_id  = %s", (tc[1],))
                        student_assignments = cur.fetchall()
                        print(student_assignments)
            session_list = {}
            class_list = []
            for cl in thier_classes:
                with get_db() as con:
                    with con.cursor() as cur:
                        cur.execute("SELECT * FROM course_sessions where course_id = %s;", (cl[0],))
                        thier_sessions = cur.fetchall()
                        tostring = str(cl[0])
                        oneout = tostring.replace('[', '')
                        twoout= oneout.replace(']', '')
                        class_list.append(twoout)
                        session_list.update( {twoout : thier_sessions})
                        for sesh in thier_sessions:
                            sesh.append(cl[1])
                        for cla in class_list:
                            with get_db() as con:
                                with con.cursor() as cur:
                                    cur.execute("SELECT assignment_name, points_earned, points_available, instructions, sesh_id FROM assignments WHERE sesh_id  = %s", (cla,))
                                    teach_assignments = cur.fetchall()


    if request.method== 'POST':
        assign_name = request.form['assign-name']
        points_ttl = request.form['points-avb']
        instructions = request.form['instructions']
        session = request.form['session_id']
        duedate = request.form['due_date']
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("INSERT INTO assignments (assignment_name, points_available, instructions, due_date, sesh_id) VALUES (%s,%s,%s,%s,%s);", (assign_name, points_ttl, instructions, duedate, session ))
                con.commit()
        return redirect(url_for('assign.assignment_page'))
    return render_template('assignments.html', teach_assignments = teach_assignments, student_assignments = student_assignments, classes=class_list, sessions=session_list)

def get_assignment(id):
    print('It gives me',id)
    with get_db() as con:
        with con.cursor() as cur:
            cur.execute('SELECT assignment_name FROM assignments WHERE instructions = %s', [id])
            assignment = cur.fetchone()
    return assignment

@bp.route('/<id>/assignment-delete', methods=('POST','GET'))
def delete_assignment(id):
    get_assignment(id)
    with get_db() as con:
        with con.cursor() as cur:
            cur.execute('DELETE FROM assignments WHERE instructions = %s',[id])
            con.commit()
    return redirect(url_for('assign.assignment_page'))
