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
        news=[
		{'title': 'Textbook Returns/Buybacks', 'body': 'The Grant Textbook Returns/Buybacks will be held in the Library Lobby beginning May 06 to May 08 from 9:00am to 6:00pm. Please bring your Student ID. All student grant Technical Program textbooks must be returned to your instructor before leaving the campus. All student grant General Education books must be returned to the Library before leaving campus or your account will be charged the average used book cost of the book.'},
		{'title': 'Community Service Deadline', 'body': 'The deadline for community service is on May 06, 2019. Please turn in your 10 hours of community service by 4:30 pm on that day or talk to our coordinator about an extension.'},
		{'title': 'Commencement 2019', 'body': 'Sophmores, make sure to pay any outstanding balances on your account before May 09, 2019. Any student with outstanding balances will not be allowed to walk at graduation.'},
		{'title': 'Grant Cars', 'body': 'Thaddeus has partnered with local dealerships to get students cars well below retail prices to get their first cars. Talk to Financial Aid to determine eligibility.'},
		{'title': 'Thaddeus Wins Award', 'body': 'Thaddeus won an award from the state for excellence in teaching and diversity. Thank you for being amazing, students.'},
		{'title': 'Alumni Dinner', 'body': 'Class of 1969 is having their Alumni banquet at the Alumni house on April 28 2019. Parking in the Kreider Lot will not be available April 27-April 28, 2019.'},
		]
        return render_template('dash.html', news=news)

    from . import sessions
    app.register_blueprint(sessions.bp)

    from . import courses
    app.register_blueprint(courses.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import schedule
    app.register_blueprint(schedule.bp)

    from . import assign
    app.register_blueprint(assign.bp)

    return app
