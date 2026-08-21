import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
SELECT
    auction_id,
    session_id,
    player_id,
    team_chiamante,
    prezzo_partenza,
    stato
FROM auctions
""")

for riga in cursor.fetchall():
    print(riga)

conn.close()