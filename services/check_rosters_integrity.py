import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

query = """
SELECT
    t.nome_squadra,
    COUNT(r.player_id) AS totale_giocatori
FROM rosters r
JOIN teams t
    ON r.team_id = t.team_id
GROUP BY t.team_id
ORDER BY t.nome_squadra
"""

cursor.execute(query)

for riga in cursor.fetchall():
    print(riga)

conn.close()