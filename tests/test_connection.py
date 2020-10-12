import pytest
from sqlsorcery import Connection, ENV_CONFIG
from sqlalchemy.exc import OperationalError


def test_sqlite_engine():
    sql = Connection(**ENV_CONFIG)
    try:
        sql.engine.connect()
    except OperationalError:
        pytest.fail("SQL Engine could not connect")
