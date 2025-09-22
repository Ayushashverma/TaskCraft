# database.py
import sqlite3
from datetime import datetime

DB_PATH = "plans.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal TEXT,
    city TEXT,
    plan TEXT,
    created_at TEXT
)
""")
conn.commit()

def save_plan(goal, plan_text, city=None):
    created_at = datetime.utcnow().isoformat()
    c.execute("INSERT INTO plans (goal, city, plan, created_at) VALUES (?, ?, ?, ?)",
              (goal, city, plan_text, created_at))
    conn.commit()
    return c.lastrowid

def get_all_plans(limit=100):
    c.execute("SELECT id, goal, city, plan, created_at FROM plans ORDER BY id DESC LIMIT ?", (limit,))
    return c.fetchall()

def get_plan_by_id(plan_id):
    c.execute("SELECT id, goal, city, plan, created_at FROM plans WHERE id = ?", (plan_id,))
    return c.fetchone()
