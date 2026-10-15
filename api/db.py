import sqlite3
from pathlib import Path

DB_PATH = str(Path(__file__).parent.parent / "game.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS players (
        name          TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        token         TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS scores (
        id     INTEGER PRIMARY KEY AUTOINCREMENT,
        player TEXT NOT NULL,
        score  INTEGER NOT NULL
    )""")
    return conn