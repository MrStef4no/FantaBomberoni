import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS audit_log (

    log_id INTEGER PRIMARY KEY AUTOINCREMENT,

    data_evento TEXT,

    squadra TEXT,

    tipo_evento TEXT,

    dettaglio TEXT
)
""")

conn.commit()

conn.close()

print("Tabella audit_log creata")