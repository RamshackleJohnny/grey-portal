import os
import psycopg2
from psycopg2.extras import DictCursor

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        # open a connection, save it to close when done
        DB_URL = os.environ.get('DATABASE_URL', None)
        if DB_URL:
            g.db = psycopg2.connect(DB_URL, sslmode='require', cursor_factory=DictCursor)
        else:
            g.db = psycopg2.connect(
                dbname=current_app.config['DB_NAME'],
                user=current_app.config['DB_USER'],
                cursor_factory=DictCursor
            )

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close() # close the connection


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        cur = db.cursor()
        cur.execute(f.read())
        cur.close()
        db.commit()

def add_user():
    db = get_db()
    cur = db.cursor()
    user_email = input("User Email: ")
    user_password = input("User Password: ")
    user_role= input("User Role (student/teacher): ")
    user_first = input("First Name: ")
    user_last = input("Last Name: ")
    cur.execute("INSERT INTO users (email, password, role, first_name, last_name) VALUES(%s, %s, %s, %s, %s)", (user_email, user_password, user_role, user_first, user_last))
    db.commit()
    cur.close()


def default_users():
    db = get_db()
    cur = db.cursor()
    user_email = 'dev@dev.com'
    user_password = 'qwerty'
    user_role= 'teacher'
    user_first = 'Teachy'
    user_last = 'McTeachface'
    cur.execute("INSERT INTO users (email, password, role, first_name, last_name) VALUES(%s, %s, %s, %s, %s)", (user_email, user_password, user_role, user_first, user_last))
    db.commit()
    user_email = 'teacher@teacher.com'
    user_password = 'teacher123'
    user_role= 'teacher'
    user_first = 'Rick'
    user_last = 'Sanchez'
    cur.execute("INSERT INTO users (email, password, role, first_name, last_name) VALUES(%s, %s, %s, %s, %s)", (user_email, user_password, user_role, user_first, user_last))
    db.commit()
    user_email = 'stu@stu.com'
    user_password = 'student1'
    user_role= 'student'
    user_first = 'Study'
    user_last = 'McStudent'
    cur.execute("INSERT INTO users (email, password, role, first_name, last_name) VALUES(%s, %s, %s, %s, %s)", (user_email, user_password, user_role, user_first, user_last))
    db.commit()
    user_email = 'morty@stu.com'
    user_password = 'student2'
    user_role= 'student'
    user_first = 'Morty'
    user_last = 'Smith'
    cur.execute("INSERT INTO users (email, password, role, first_name, last_name) VALUES(%s, %s, %s, %s, %s)", (user_email, user_password, user_role, user_first, user_last))
    db.commit()
    user_email = 'jerry@stu.com'
    user_password = 'student3'
    user_role= 'student'
    user_first = 'Jerry'
    user_last = 'Smith'
    cur.execute("INSERT INTO users (email, password, role, first_name, last_name) VALUES(%s, %s, %s, %s, %s)", (user_email, user_password, user_role, user_first, user_last))
    db.commit()
    user_email = 'michael@stu.com'
    user_password = 'student4'
    user_role= 'student'
    user_first = 'Michael'
    user_last = 'Withab'
    cur.execute("INSERT INTO users (email, password, role, first_name, last_name) VALUES(%s, %s, %s, %s, %s)", (user_email, user_password, user_role, user_first, user_last))
    db.commit()
    user_email = 'bichael@stu.com'
    user_password = 'student5'
    user_role= 'student'
    user_first = 'Bichael'
    user_last = 'Withab'
    cur.execute("INSERT INTO users (email, password, role, first_name, last_name) VALUES(%s, %s, %s, %s, %s)", (user_email, user_password, user_role, user_first, user_last))
    db.commit()
    course_name = 'Git'
    course_desc = 'Basics of Git, including workflow'
    course_num = '8675'
    cursor.execute("INSERT INTO courses (course_name, description, course_number, teacher_id) VALUES (%s, %s, %s, %s)", (course_name, course_desc, course_num, 1))
    db.commit()
    course_name = 'SoundCloud Rapping'
    course_desc = "Danny would be mad at me if I didn't put this in"
    course_num = '3090'
    cursor.execute("INSERT INTO courses (course_name, description, course_number, teacher_id) VALUES (%s, %s, %s, %s)", (course_name, course_desc, course_num, 1))
    db.commit()
    course_name = 'Yes'
    course_desc = 'A class on positivity'
    course_num = '0666'
    cursor.execute("INSERT INTO courses (course_name, description, course_number, teacher_id) VALUES (%s, %s, %s, %s)", (course_name, course_desc, course_num, 1))
    db.commit()
    cur.close()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

@click.command('add-user')
@with_appcontext
def add_user_command():
    """Create new user"""
    add_user()
    click.echo('Created user.')

@click.command('defaults')
@with_appcontext
def default_users_command():
    """Adds Default Testing Users"""
    default_users()
    click.echo('Created default users.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(add_user_command)
    app.cli.add_command(default_users_command)
