import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("DELETE FROM public_bids")
cursor.execute("DELETE FROM auctions")

conn.commit()

print("Aste eliminate")

conn.close()