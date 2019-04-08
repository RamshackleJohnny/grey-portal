import psycopg2
import pytest

from portal.db import get_db


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db(), 'get_db should always return the same connection'

    with pytest.raises(psycopg2.InterfaceError) as e:
        cur = db.cursor()
        cur.execute('SELECT 1')

    assert 'closed' in str(e), 'connection should be closed after app context'


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('portal.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called

