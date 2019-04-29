# test_courses.py
from flask import request
import pytest

from portal import create_app
from portal.db import get_db
from portal.auth import login_required



def test_test_page(client):
    response= client.get('/testing')
    assert response.status_code==200

def test_course_page(client):
    response= client.get('/courses')
    assert response.status_code==302

def test_update_course(client):
    response= client.get('/1/course-update')
    assert response.status_code==302

def test_delete_course(client):
    response= client.get('/1/course-delete')
    assert response.status_code==302

# TODO: Test get_course. -Danny.
def test_get_course(id):
    id=1
    assert course
