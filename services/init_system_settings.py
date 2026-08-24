import sqlite3

conn = sqlite3.connect("database/fantalega.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS system_settings (

    setting_key TEXT PRIMARY KEY,
    setting_value TEXT
)
""")

cursor.execute("""
INSERT OR IGNORE INTO system_settings
VALUES (
    'MARKET_OVERRIDE',
    'AUTO'
)
""")

cursor.execute("""
INSERT OR IGNORE INTO system_settings
VALUES (
    'MARKET_PHASE_OVERRIDE',
    'AUTO'
)
""")

cursor.execute("""
INSERT OR IGNORE INTO system_settings
VALUES (
    'LAST_NOTIFIED_PHASE',
    'CHIUSO'
)
""")

conn.commit()
conn.close()

print("system_settings creata")
