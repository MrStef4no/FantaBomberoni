import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
UPDATE prizes
SET team_id = NULL
""")

conn.commit()

conn.close()

print("Premi azzerati")