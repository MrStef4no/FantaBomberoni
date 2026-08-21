import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
SELECT
    round_id,
    auction_id,
    round_number,
    stato,
    offerta_minima
FROM sealed_rounds
ORDER BY round_id
""")

for riga in cursor.fetchall():
    print(riga)

conn.close()