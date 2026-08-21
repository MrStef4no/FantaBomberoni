import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS prizes (
    prize_id INTEGER PRIMARY KEY AUTOINCREMENT,
    competizione TEXT,
    ranking INTEGER,
    premio REAL,
    team_id INTEGER
)
""")

conn.commit()

conn.close()

print("Tabella prizes creata")