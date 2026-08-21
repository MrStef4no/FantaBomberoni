import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
SELECT team_id,
       nome_squadra,
       budget_residuo,
       cambi_residui
FROM teams
""")

for squadra in cursor.fetchall():
    print(squadra)

conn.close()