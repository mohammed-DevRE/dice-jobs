import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.getenv("DATABASE_PATH", "/data/jobs.db")


@contextmanager
def connection():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db():
    with connection() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
          id INTEGER PRIMARY KEY,
          source TEXT NOT NULL,
          title TEXT NOT NULL,
          company TEXT NOT NULL DEFAULT '',
          url TEXT NOT NULL UNIQUE,
          status TEXT NOT NULL DEFAULT 'pending',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS runs (
          id INTEGER PRIMARY KEY,
          source TEXT NOT NULL,
          status TEXT NOT NULL,
          detail TEXT NOT NULL DEFAULT '',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)


def add_job(source, title, company, url):
    with connection() as con:
        con.execute(
            "INSERT OR IGNORE INTO jobs(source,title,company,url) VALUES(?,?,?,?)",
            (source, title[:300], company[:300], url),
        )


def set_status(job_id, status):
    if status not in {"pending", "approved", "rejected", "applied"}:
        raise ValueError("invalid status")
    with connection() as con:
        con.execute(
            "UPDATE jobs SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (status, job_id),
        )


def list_jobs():
    with connection() as con:
        return con.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()


def log_run(source, status, detail=""):
    with connection() as con:
        con.execute("INSERT INTO runs(source,status,detail) VALUES(?,?,?)", (source, status, detail[:1000]))

