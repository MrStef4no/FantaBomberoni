import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

query = """
SELECT
    t.nome_squadra,
    p.nome,
    p.ruolo
FROM rosters r
INNER JOIN teams t
    ON r.team_id = t.team_id
INNER JOIN players p
    ON r.player_id = p.player_id
"""

cursor.execute(query)

risultati = cursor.fetchall()

print("Numero record:", len(risultati))

for riga in risultati:
    print(riga)

conn.close()
import os

print("Database usato:")
print(os.path.abspath("../database/fantalega.db"))