import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

query = """
SELECT
    COUNT(*)
FROM rosters r
JOIN players p
    ON r.player_id = p.player_id
"""

cursor.execute(query)

totale = cursor.fetchone()[0]

print("Giocatori delle rose presenti nel nuovo listone:", totale)

conn.close()