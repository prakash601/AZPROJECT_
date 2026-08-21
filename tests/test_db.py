"""Tests for db.py – connection pool."""
import pytest
from unittest import mock
from contextlib import contextmanager


def test_get_conn_commit_on_success():
    import db

    mock_conn = mock.MagicMock()
    mock_pool = mock.MagicMock()
    mock_pool.getconn.return_value = mock_conn

    with mock.patch.object(db, "_pool", mock_pool), \
         mock.patch("db.register_vector") as mock_reg:
        with db.get_conn() as conn:
            assert conn is mock_conn
            mock_reg.assert_called_once_with(mock_conn)
        mock_conn.commit.assert_called_once()
        mock_pool.putconn.assert_called_once_with(mock_conn)


def test_get_conn_rollback_on_exception():
    import db

    mock_conn = mock.MagicMock()
    mock_pool = mock.MagicMock()
    mock_pool.getconn.return_value = mock_conn

    with mock.patch.object(db, "_pool", mock_pool), \
         mock.patch("db.register_vector"):
        with pytest.raises(RuntimeError):
            with db.get_conn() as conn:
                raise RuntimeError("boom")

        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()
        mock_pool.putconn.assert_called_once_with(mock_conn)


def test_get_cursor_commit_true():
    import db

    mock_cur = mock.MagicMock()
    mock_conn = mock.MagicMock()
    mock_conn.cursor.return_value = mock_cur

    @contextmanager
    def fake_get_conn():
        yield mock_conn

    with mock.patch("db.get_conn", fake_get_conn):
        with db.get_cursor(commit=True) as cur:
            assert cur is mock_cur
        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()


def test_get_cursor_commit_false():
    import db

    mock_cur = mock.MagicMock()
    mock_conn = mock.MagicMock()
    mock_conn.cursor.return_value = mock_cur

    @contextmanager
    def fake_get_conn():
        yield mock_conn

    with mock.patch("db.get_conn", fake_get_conn):
        with db.get_cursor(commit=False) as cur:
            pass
        mock_conn.commit.assert_not_called()
        mock_cur.close.assert_called_once()


def test_get_cursor_always_closes_even_on_error():
    import db

    mock_cur = mock.MagicMock()
    mock_conn = mock.MagicMock()
    mock_conn.cursor.return_value = mock_cur

    @contextmanager
    def fake_get_conn():
        yield mock_conn

    with mock.patch("db.get_conn", fake_get_conn):
        with pytest.raises(ValueError):
            with db.get_cursor() as cur:
                raise ValueError("fail")
        mock_cur.close.assert_called_once()
