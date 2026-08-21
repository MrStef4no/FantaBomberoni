import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
SELECT team_id, nome_squadra
FROM teams
ORDER BY team_id
""")

for team in cursor.fetchall():
    print(team)

conn.close()