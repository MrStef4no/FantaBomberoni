import sqlite3

conn = sqlite3.connect("database/fantalega.db")
cur = conn.cursor()

cur.execute("SELECT * FROM system_settings")
print(cur.fetchall())

conn.close()