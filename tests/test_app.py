# test_app.py
from flask import request
import pytest

from portal import create_app
from portal.db import get_db
def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

def test_index(client):
    response = client.get('/')
    assert b'<h1>TSCT Portal</h1>' in response.data
    # There is NO nav bar if we're not logged in.
    assert b'<nav>' not in response.data

@pytest.mark.parametrize(('email', 'password', 'message'), (
    ('Nah@.vom', 'yeet', b'Username or password is incorrect'),
    ('not@it', 'wrong', b'Username or password is incorrect'),
))
def test_register_validate_input(client, email, password, message):
    response = client.post(
        '/',
        data={'email': email, 'password': password}
    )
    assert message in response.data

def test_login(client, app):
    assert client.get('/auth/login').status_code == 200
    response = client.post(
        '/', data={'email': 's@s', 'password': 's'}
    )
    with app.app_context():
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = 's@s'")
                course = cur.fetchone()
                assert course is None

    # Later on this will change.
def test_logout(client):
    response=client.get('/logout')
    assert response.status_code==302
