import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

query = """
SELECT
    p.nome,
    p.ruolo,
    p.squadra_serie_a
FROM players p
LEFT JOIN rosters r
    ON p.player_id = r.player_id
WHERE r.player_id IS NULL
ORDER BY p.nome
"""

cursor.execute(query)

svincolati = cursor.fetchall()

print("Totale svincolati:", len(svincolati))
print()

for giocatore in svincolati[:30]:
    print(giocatore)

conn.close()