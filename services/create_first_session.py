import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
DELETE FROM market_sessions
""")

cursor.execute("""
INSERT INTO market_sessions (
    descrizione,
    data_apertura,
    data_chiusura,
    stato
)
VALUES (?, ?, ?, ?)
""", (
    "Mercato Test",
    "2026-07-28 00:01",
    "2026-07-31 17:00",
    "APERTA"
))

conn.commit()

print("Sessione creata")

conn.close()