# services/reset_sealed_rounds.py

import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("DELETE FROM round_participants")
cursor.execute("DELETE FROM sealed_rounds")
cursor.execute("DELETE FROM sealed_bids")

conn.commit()

print("Round e buste azzerati")

conn.close()