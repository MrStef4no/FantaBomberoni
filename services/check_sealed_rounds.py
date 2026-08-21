import sqlite3

conn = sqlite3.connect("database/fantalega.db")
cursor = conn.cursor()

print("=== sealed_rounds ===")

cursor.execute("""
PRAGMA table_info(sealed_rounds)
""")

for riga in cursor.fetchall():
    print(riga)

print("\n=== round_participants ===")

cursor.execute("""
PRAGMA table_info(round_participants)
""")

for riga in cursor.fetchall():
    print(riga)

conn.close()