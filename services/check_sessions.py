import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
SELECT
    session_id,
    descrizione,
    data_apertura,
    data_chiusura,
    stato
FROM market_sessions
""")

for riga in cursor.fetchall():
    print(riga)

conn.close()