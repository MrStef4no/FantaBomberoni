import sqlite3
import os

db = "../database/fantalega.db"

print("Database:", os.path.abspath(db))

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

cursor.execute("SELECT * FROM rosters")

righe = cursor.fetchall()

print("Numero righe:", len(righe))

for riga in righe:
    print(riga)

conn.close()