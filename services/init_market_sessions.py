import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS market_sessions (

    session_id INTEGER PRIMARY KEY AUTOINCREMENT,

    data_inizio TEXT NOT NULL,

    data_fine TEXT NOT NULL,

    stato TEXT NOT NULL
)
""")

conn.commit()

conn.close()

print("Tabella market_sessions creata")