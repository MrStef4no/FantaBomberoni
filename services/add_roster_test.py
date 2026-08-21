import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

# Cerca Soulè
cursor.execute("""
SELECT player_id, nome
FROM players
WHERE nome LIKE '%Soul%'
""")

giocatore = cursor.fetchone()

print("Giocatore trovato:", giocatore)

if giocatore:

    player_id = giocatore[0]

    cursor.execute("""
    INSERT INTO rosters (
        team_id,
        player_id,
        attivo,
        bloccato_svincolo
    )
    VALUES (?, ?, ?, ?)
    """, (
        1,      # Team 1
        player_id,
        1,
        0
    ))

    conn.commit()

    print("Giocatore inserito nella rosa")

conn.close()
import os

print("Database usato:")
print(os.path.abspath("../database/fantalega.db"))