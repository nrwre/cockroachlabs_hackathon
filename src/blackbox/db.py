"""Database access — a thin helper around psycopg 3 for talking to CockroachDB.

CockroachDB speaks the PostgreSQL wire protocol, so the same psycopg driver that
works with Postgres works here unchanged. That's the whole point: standard tools,
distributed + always-on database underneath.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import psycopg

from .config import get_settings


@contextmanager
def connect() -> Iterator[psycopg.Connection]:
    """Open a connection to CockroachDB and guarantee it gets closed.

    Usage:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                print(cur.fetchone())
    """
    settings = get_settings()
    conn = psycopg.connect(settings.database_url)
    try:
        yield conn
    finally:
        conn.close()


def ping() -> bool:
    """Return True if we can reach the database. A tiny smoke test for setup."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1")
        return cur.fetchone() == (1,)
