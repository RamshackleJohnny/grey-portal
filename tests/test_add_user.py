import psycopg2
import pytest


conn = psycopg2.connect(database = "portal")
cur = conn.cursor()


def insert_into_database():
    assert insert_into_database(23562, "newteacher@newcollege.edu", user_password, "teacher") == "user added"
