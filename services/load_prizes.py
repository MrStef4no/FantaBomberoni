import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("DELETE FROM prizes")

premi = [
    ("Serie A", 1, 1400),
    ("Serie A", 2, 600),
    ("Serie A", 3, 300),
    ("Coppa Italia", 1, 450),
    ("Champions", 1, 450),
    ("Europa", 1, 150),
    ("Scontri", 1, 150),
    ("Highlander", 1, 100)
]

for competizione, ranking, premio in premi:

    cursor.execute("""
    INSERT INTO prizes (
        competizione,
        ranking,
        premio,
        team_id
    )
    VALUES (?, ?, ?, NULL)
    """, (
        competizione,
        ranking,
        premio
    ))

conn.commit()

conn.close()

print("Premi caricati")