import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

query = """
SELECT
    t.nome_squadra,
    r.player_id
FROM rosters r
JOIN teams t
    ON r.team_id = t.team_id
LEFT JOIN players p
    ON r.player_id = p.player_id
WHERE p.player_id IS NULL
ORDER BY t.nome_squadra
"""

cursor.execute(query)

righe = cursor.fetchall()

print("Totale giocatori mancanti:", len(righe))
print()

for riga in righe:
    print(riga)

conn.close()