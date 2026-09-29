import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from app.config import get_settings


def _connect():
    path = Path(get_settings().database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with _connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, age INTEGER NOT NULL,
            goal TEXT NOT NULL, level TEXT NOT NULL, days_per_week INTEGER NOT NULL,
            equipment TEXT NOT NULL, constraints_text TEXT NOT NULL DEFAULT '',
            plan_json TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        db.execute("""CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            note TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")


def create_user(profile: dict, plan: dict) -> int:
    with _connect() as db:
        cur = db.execute("""INSERT INTO users(name,age,goal,level,days_per_week,equipment,constraints_text,plan_json)
            VALUES(?,?,?,?,?,?,?,?)""", (profile["name"], profile["age"], profile["goal"], profile["level"],
            profile["days_per_week"], profile["equipment"], profile.get("constraints", ""), json.dumps(plan)))
        return int(cur.lastrowid)


def get_user(user_id: int):
    with _connect() as db:
        row = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if not row:
            return None
        item = dict(row)
        item["plan"] = json.loads(item.pop("plan_json"))
        item["feedback"] = [dict(x) for x in db.execute(
            "SELECT note,created_at FROM feedback WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()]
        return item


def update_plan(user_id: int, plan: dict, note: str):
    with _connect() as db:
        cur = db.execute("UPDATE users SET plan_json=? WHERE id=?", (json.dumps(plan), user_id))
        if cur.rowcount == 0:
            return False
        db.execute("INSERT INTO feedback(user_id,note) VALUES(?,?)", (user_id, note))
        return True


def list_users():
    with _connect() as db:
        return [dict(row) for row in db.execute(
            "SELECT id,name,age,goal,level,days_per_week,created_at FROM users ORDER BY id DESC").fetchall()]
