import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
SELECT
    auction_id,
    team_id,
    ha_abbandonato
FROM auction_participants
ORDER BY auction_id, team_id
""")

for riga in cursor.fetchall():
    print(riga)

conn.close()