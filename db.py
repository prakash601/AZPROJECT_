"""
Database connection pool for PostgreSQL with pgvector support.

The pool is created lazily on first use (not at import) so a transient
DB outage never crashes app startup, with one retry that rebuilds the
pool if the existing connections have gone stale.
"""
import logging
import os
import threading

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from pgvector.psycopg2 import register_vector
from contextlib import contextmanager
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

DB_CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))

_pool = None
_pool_lock = threading.Lock()


def _create_pool():
    logger.info("Creating database connection pool...")
    return ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "azproject"),
        user=os.getenv("DB_USER", "azuser"),
        password=os.getenv("DB_PASSWORD", "azpass"),
        connect_timeout=DB_CONNECT_TIMEOUT,
    )


def _get_pool():
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = _create_pool()
    return _pool


def _reset_pool(pool):
    """Close a broken pool and force a fresh one on next checkout."""
    global _pool
    with _pool_lock:
        if _pool is pool:
            try:
                pool.closeall()
            except Exception:
                logger.exception("Error closing stale connection pool")
            _pool = None


@contextmanager
def get_conn():
    """Get a live connection from the pool, retrying once on failure."""
    conn = None
    owner = None
    last_err = None
    for attempt in (1, 2):
        try:
            owner = _get_pool()
            conn = owner.getconn()
            register_vector(conn)  # Required for vector type support
            break
        except psycopg2.Error as e:
            last_err = e
            logger.warning("DB connection failed (attempt %d/2): %s",
                           attempt, e)
            conn = None
            if owner is not None:
                _reset_pool(owner)
                owner = None
    if conn is None:
        raise last_err

    try:
        yield conn
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except psycopg2.Error:
            logger.exception("Rollback failed on broken connection")
        raise
    finally:
        try:
            owner.putconn(conn)
        except Exception:
            logger.exception("Failed returning connection to pool")


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
