import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

# Svuota la tabella
cursor.execute("DELETE FROM teams")

squadre = [
    "Borussia Baggins",
    "FC La urina",
    "Osasuca",
    "A.C. avanti chisto",
    "I Calypso Boys",
    "SKIBIDI BRONDBY",
    "Stazi boys",
    "Il Re del Fantacalcio",
    "Milancello",
    "Faggiani Tattici Nucleari",
    "Inter-Pol",
    "Rivolta al Re"
]

for squadra in squadre:

    cursor.execute("""
        INSERT INTO teams (
            nome_squadra,
            manager,
            budget_residuo,
            fase_cambi,
            cambi_residui
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        squadra,
        squadra,
        500,
        1,
        10
    ))

conn.commit()

print("12 squadre importate")

conn.close()