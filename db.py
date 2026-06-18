"""
Database connection pool for PostgreSQL with pgvector support.
"""
import os
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from pgvector.psycopg2 import register_vector
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

pool = ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
    database=os.getenv("DB_NAME", "azproject"),
    user=os.getenv("DB_USER", "azuser"),
    password=os.getenv("DB_PASSWORD", "azpass")
)


@contextmanager
def get_conn():
    """Get a connection from the pool with pgvector type support registered."""
    conn = pool.getconn()
    register_vector(conn)  # Required for vector type support
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


@contextmanager
def get_cursor(commit=True):
    """Get a cursor from a pooled connection."""
    with get_conn() as conn:
        cur = conn.cursor()
        try:
            yield cur
            if commit:
                conn.commit()
        finally:
            cur.close()
