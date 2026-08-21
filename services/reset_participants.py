import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
DELETE FROM auction_participants
""")

conn.commit()

print("Partecipanti azzerati")

conn.close()