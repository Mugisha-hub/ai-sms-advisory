import sqlite3
from datetime import datetime

DB_PATH = "messages.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            text TEXT,
            reply TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_message(phone, text, reply):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (phone, text, reply, timestamp) VALUES (?, ?, ?, ?)",
        (phone, text, reply, datetime.now())
    )
    conn.commit()
    conn.close()
