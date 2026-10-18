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
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            player      TEXT NOT NULL,
            score       INTEGER NOT NULL,
            boss_beaten INTEGER NOT NULL DEFAULT 0
        )""")
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(scores)")]
    if "boss_beaten" not in cols:
        conn.execute(
            "ALTER TABLE scores ADD COLUMN boss_beaten INTEGER NOT NULL DEFAULT 0"
        )
    return conn