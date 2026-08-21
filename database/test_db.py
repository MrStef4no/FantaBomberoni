import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
""")

for tabella in cursor.fetchall():
    print(tabella)

conn.close()