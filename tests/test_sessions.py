# test_courses.py
from flask import request
import pytest

from portal import create_app
from portal.db import get_db
from portal.auth import login_required


def test_sessions(client, auth):
    response= client.get('/sessions')
    auth.login()
    assert response.status_code==200

def test_update_session(client, auth):
    response= client.get('/update-session')
    auth.login()
    assert response.status_code==200
