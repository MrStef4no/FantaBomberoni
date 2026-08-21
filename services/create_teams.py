import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

# Pulisce eventuali squadre già presenti
cursor.execute("DELETE FROM teams")

squadre = [
    "Squadra 1",
    "Squadra 2",
    "Squadra 3",
    "Squadra 4",
    "Squadra 5",
    "Squadra 6",
    "Squadra 7",
    "Squadra 8",
    "Squadra 9",
    "Squadra 10",
    "Squadra 11",
    "Squadra 12"
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

print("12 squadre create")

conn.close()