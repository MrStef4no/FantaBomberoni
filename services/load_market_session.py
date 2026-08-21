import sqlite3

conn = sqlite3.connect("database/fantalega.db")

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
VALUES (
    'Sessione Agosto 2026',
    '2026-08-18',
    '2026-08-21',
    'APERTA'
)
""")

conn.commit()

conn.close()

print("Sessione caricata")