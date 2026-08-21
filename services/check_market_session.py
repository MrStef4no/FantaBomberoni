import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
PRAGMA table_info(market_results)
""")

for riga in cursor.fetchall():
    print(riga)

conn.close()
