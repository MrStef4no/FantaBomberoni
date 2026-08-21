import sqlite3
import pandas as pd

EXCEL = "data/Quotazioni_Fantacalcio_Stagione_2026_27.xlsx"
DATABASE = "database/fantalega.db"

# Lettura file ufficiale
df = pd.read_excel(
    EXCEL,
    sheet_name="Tutti",
    header=1
)

# Manteniamo solo le colonne utili
df = df[
    ["Id", "R", "RM", "Nome", "Squadra", "Qt.A", "FVM"]
].copy()

# Rinominiamo le colonne nel formato della nostra app
df.columns = [
    "ID",
    "Ruolo",
    "Ruolo_Dettaglio",
    "Nome",
    "Squadra",
    "Quotazione",
    "FVM"
]

conn = sqlite3.connect(r"database/fantalega.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM players")

for _, row in df.iterrows():

    cursor.execute("""
        INSERT INTO players (
            player_id,
            nome,
            ruolo,
            ruolo_dettaglio,
            squadra_serie_a,
            quotazione,
            fvm,
            disponibile_mercato
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        int(row["ID"]),
        str(row["Nome"]),
        str(row["Ruolo"]),
        str(row["Ruolo_Dettaglio"]),
        str(row["Squadra"]),
        float(row["Quotazione"]),
        float(row["FVM"]),
        1
    ))

conn.commit()

cursor.execute("SELECT COUNT(*) FROM players")

totale = cursor.fetchone()[0]

print(f"Giocatori importati: {totale}")

conn.close()