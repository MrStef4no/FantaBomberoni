import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("DELETE FROM round_participants")
cursor.execute("DELETE FROM sealed_bids")
cursor.execute("DELETE FROM sealed_rounds")

conn.commit()

print("Spareggi azzerati")

conn.close()