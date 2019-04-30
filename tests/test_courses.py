# test_courses.py
from flask import request
import pytest

from portal import create_app
from portal.db import get_db
from portal.auth import login_required



def test_test_page(client):
    response= client.get('/testing')
    assert response.status_code==200

def test_course_page(client, auth):
    response= client.get('/courses')
    auth.login()
    assert b"<title>Redirecting...</title>" in response.data
    assert response.status_code==302

def test_update_course(client, auth):
    response= client.get('/1/course-update')
    auth.login()
    assert response.status_code==302

def test_delete_course(client,auth):
    response= client.get('/1/course-delete')
    auth.login()
    assert response.status_code==302
