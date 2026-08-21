import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
SELECT
    team_id,
    nome_squadra,
    budget_residuo,
    cambi_residui
FROM teams
ORDER BY team_id
""")

for riga in cursor.fetchall():
    print(riga)

conn.close()