import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

print("ROSTERS")
cursor.execute("""
PRAGMA table_info(rosters)
""")

for riga in cursor.fetchall():
    print(riga)

print()

print("PLAYERS")
cursor.execute("""
PRAGMA table_info(players)
""")

for riga in cursor.fetchall():
    print(riga)

conn.close()