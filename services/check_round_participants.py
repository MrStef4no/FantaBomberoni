import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
SELECT COUNT(*)
FROM round_participants
""")

totale = cursor.fetchone()[0]

print("Record trovati:", totale)
print()

cursor.execute("""
SELECT
    round_id,
    team_id
FROM round_participants
ORDER BY round_id, team_id
""")

for riga in cursor.fetchall():
    print(riga)

conn.close()