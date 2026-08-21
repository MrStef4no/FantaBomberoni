import sqlite3
import pandas as pd

# -------------------------
# FILE
# -------------------------

EXCEL_FILE = "../data/Rose_bomberoni 2025-26.xlsx"
DB_FILE = "../database/fantalega.db"

# -------------------------
# LETTURA EXCEL
# -------------------------

df = pd.read_excel(EXCEL_FILE)

# -------------------------
# DATABASE
# -------------------------

conn = sqlite3.connect(r"database/fantalega.db")
cursor = conn.cursor()

# pulizia rosters
cursor.execute("DELETE FROM rosters")

current_team = None

for _, row in df.iterrows():

    col1 = str(row.iloc[0]).strip()

    # ignora righe vuote
    if col1 == "nan":
        continue

    # ignora intestazioni
    if col1 == "Ruolo":
        continue

    # ignora url
    if col1.startswith("http"):
        continue

    # ignora nota iniziale
    if col1.startswith("*"):
        continue

    # fine squadra
    if "Crediti Residui:" in col1:
        current_team = None
        continue

    # nuova squadra
    if pd.isna(row.iloc[1]):
        current_team = col1
        print(f"Squadra trovata: {current_team}")
        continue

    # giocatore
    if current_team:

        nome_giocatore = str(row.iloc[1]).strip()

        # id squadra
        cursor.execute("""
        SELECT team_id
        FROM teams
        WHERE nome_squadra = ?
        """, (current_team,))

        team = cursor.fetchone()

        if not team:
            print(f"Squadra non trovata: {current_team}")
            continue

        team_id = team[0]

        # id giocatore
        cursor.execute("""
        SELECT player_id
        FROM players
        WHERE nome = ?
        """, (nome_giocatore,))

        player = cursor.fetchone()

        if not player:
            print(f"Giocatore NON trovato: {nome_giocatore}")
            continue

        player_id = player[0]

        cursor.execute("""
        INSERT INTO rosters (
            team_id,
            player_id,
            attivo,
            bloccato_svincolo
        )
        VALUES (?, ?, ?, ?)
        """, (
            team_id,
            player_id,
            1,
            0
        ))

conn.commit()

# Conteggio finale
cursor.execute("""
SELECT COUNT(*)
FROM rosters
""")

totale = cursor.fetchone()[0]

print()
print(f"Giocatori importati nelle rose: {totale}")

conn.close()