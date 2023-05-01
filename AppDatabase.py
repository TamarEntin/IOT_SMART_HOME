import sqlite3


def init_db():
    conn = sqlite3.connect("AquaAlert.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()


def save_message(message):
    conn = sqlite3.connect("AquaAlert.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (message, timestamp) VALUES (?, datetime('now'))", (message,))
    conn.commit()
    conn.close()


def fetch_data():
    conn = sqlite3.connect("AquaAlert.db")
    c = conn.cursor()
    c.execute("SELECT message, timestamp FROM messages")
    data = c.fetchall()
    conn.close()
    return data