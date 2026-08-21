import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

nome = input("Nome giocatore: ")

cursor.execute("""
SELECT player_id,
       nome,
       ruolo,
       squadra_serie_a
FROM players
WHERE nome LIKE ?
""", (f"%{nome}%",))

risultati = cursor.fetchall()

for r in risultati:
    print(r)

conn.close()