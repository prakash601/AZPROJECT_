"""Shared fixtures – mock DB pool before any app module is imported."""
import sys
from unittest import mock
import pytest

# ----------------------------------------------------------------------
# Patch psycopg2 pool globally BEFORE importing db/main/search/...
# db.py creates ThreadedConnectionPool at import time which would try to
# connect to Supabase and fail offline. We replace it with a MagicMock.
# ----------------------------------------------------------------------
_mock_pool = mock.MagicMock(name="ThreadedConnectionPool")
_mock_pool_getconn = _mock_pool.getconn
_mock_pool_putconn = _mock_pool.putconn

# Patch the class so db.pool becomes the mock instance
_patcher_pool = mock.patch("psycopg2.pool.ThreadedConnectionPool", return_value=_mock_pool)
_patcher_pool.start()

# Also prevent register_vector from needing a real connection
_patcher_register = mock.patch("pgvector.psycopg2.register_vector", return_value=None)
_patcher_register.start()

# Prevent NLTK download attempts at import (correct.py:7-12)
_patcher_nltk_find = mock.patch("nltk.data.find", return_value=True)
_patcher_nltk_find.start()
_patcher_nltk_download = mock.patch("nltk.download", return_value=True)
_patcher_nltk_download.start()

# Ensure project root is on sys.path (pytest.ini pythonpath does this too)
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture
def mock_pool():
    """Return the global mocked pool instance."""
    return _mock_pool


@pytest.fixture
def mock_cursor():
    """Create a fresh MagicMock cursor + connection pair."""
    mock_cur = mock.MagicMock()
    # mogrify must return bytes like psycopg2 does
    mock_cur.mogrify.side_effect = lambda query, params: b"(%s, %s, %s, %s)" % tuple(
        b"'%s'" % str(p).encode() if isinstance(p, str) else b"1" for p in params
    )
    # For tests that want realistic mogrify: override side_effect
    mock_cur.fetchall.return_value = []
    mock_cur.fetchone.return_value = [0]
    mock_cur.execute.return_value = None
    mock_cur.executemany.return_value = None
    mock_cur.close.return_value = None

    mock_conn = mock.MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_conn.commit.return_value = None
    mock_conn.rollback.return_value = None

    return mock_cur, mock_conn


@pytest.fixture
def mock_get_cursor(mock_cursor):
    """Patch db.get_cursor to yield mock_cursor."""
    mock_cur, mock_conn = mock_cursor
    # Build a contextmanager that yields mock_cur
    from contextlib import contextmanager

    @contextmanager
    def _fake_get_cursor(commit=True):
        yield mock_cur

    # Patch in all modules that import get_cursor
    patches = []
    for mod in ["db", "search", "correct", "migrate", "generate_embeddings"]:
        try:
            p = mock.patch(f"{mod}.get_cursor", _fake_get_cursor)
            p.start()
            patches.append(p)
        except ModuleNotFoundError:
            continue
    # Also patch db.get_conn if needed
    @contextmanager
    def _fake_get_conn():
        yield mock_conn

    p_conn = mock.patch("db.get_conn", _fake_get_conn)
    p_conn.start()
    patches.append(p_conn)

    yield mock_cur, mock_conn

    for p in patches:
        p.stop()


@pytest.fixture
def client(mock_get_cursor):
    """FastAPI TestClient with DB mocked."""
    # mock_get_cursor already patches db; import app after patching
    from fastapi.testclient import TestClient
    import main

    with TestClient(main.app) as c:
        yield c


@pytest.fixture(autouse=True)
def reset_words_cache():
    """Reset correct.WORDS_CACHE between tests."""
    yield
    try:
        import correct
        correct.WORDS_CACHE = None
    except Exception:
        pass


@pytest.fixture(autouse=True)
def reset_search_model():
    """Reset lazy ONNX globals."""
    yield
    try:
        import search
        search._tokenizer = None
        search._model = None
    except Exception:
        pass
