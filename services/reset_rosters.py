import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM rosters")

conn.commit()

print("Tabella rosters svuotata")

conn.close()