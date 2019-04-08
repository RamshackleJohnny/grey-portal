import os

import pytest

from portal import create_app
from portal.db import get_db, init_db


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'DB_NAME': 'portal_test',
        'DB_USER': 'portal_user',
    })

    with app.app_context():
        init_db()

        with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
            con = get_db()
            cur = con.cursor()
            cur.execute(f.read())
            cur.close()
            con.commit()
            con.close()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()

