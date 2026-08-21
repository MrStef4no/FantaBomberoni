import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    user_id INTEGER PRIMARY KEY AUTOINCREMENT,

    nome_account TEXT UNIQUE,

    team_id INTEGER,

    password TEXT,

    is_admin INTEGER DEFAULT 0,

    attivo INTEGER DEFAULT 1
)
""")

conn.commit()
conn.close()

print("Tabella users creata")