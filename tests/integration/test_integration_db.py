"""Integration tests requiring real PostgreSQL + pgvector.

Run: docker compose up -d postgres && pytest -m integration -v

Skipped automatically if DB not reachable.
"""
import os
import pytest
import psycopg2

pytestmark = pytest.mark.integration


def _can_connect():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "azproject"),
            user=os.getenv("DB_USER", "azuser"),
            password=os.getenv("DB_PASSWORD", "azpass"),
            connect_timeout=2,
        )
        conn.close()
        return True
    except Exception:
        return False


@pytest.fixture(scope="module")
def real_conn():
    if not _can_connect():
        pytest.skip("Postgres not reachable – skipping integration tests (run docker compose up -d postgres)")
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "azproject"),
        user=os.getenv("DB_USER", "azuser"),
        password=os.getenv("DB_PASSWORD", "azpass"),
    )
    # Ensure extensions and schema exist
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(open("init.sql").read())
    yield conn
    conn.close()


def test_extensions_exist(real_conn):
    with real_conn.cursor() as cur:
        cur.execute("SELECT extname FROM pg_extension WHERE extname IN ('vector','pg_trgm')")
        rows = cur.fetchall()
        names = {r[0] for r in rows}
        assert "vector" in names
        assert "pg_trgm" in names


def test_problems_table_exists(real_conn):
    with real_conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.problems')")
        assert cur.fetchone()[0] is not None


def test_search_vector_generated(real_conn):
    # Insert a dummy row and check search_vector is populated
    with real_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO problems (platform, title, url, description)
            VALUES ('test', 'Hello World', 'https://example.test/hello', 'desc for fts')
            ON CONFLICT (url) DO NOTHING
            RETURNING id, search_vector
        """)
        row = cur.fetchone()
        if row:
            assert row[1] is not None
        real_conn.commit()
        # cleanup
        cur.execute("DELETE FROM problems WHERE url='https://example.test/hello'")
        real_conn.commit()


def test_trigram_similarity(real_conn):
    with real_conn.cursor() as cur:
        cur.execute("SELECT similarity('hello', 'hallo')")
        sim = cur.fetchone()[0]
        assert 0 <= sim <= 1


def test_vector_type_exists(real_conn):
    with real_conn.cursor() as cur:
        cur.execute("SELECT typname FROM pg_type WHERE typname='vector'")
        assert cur.fetchone() is not None
