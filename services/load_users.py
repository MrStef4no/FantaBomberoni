import sqlite3

conn = sqlite3.connect("database/fantalega.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM users")

# ADMIN
cursor.execute("""
INSERT INTO users (
    nome_account,
    team_id,
    password,
    is_admin
)
VALUES (
    'ADMIN',
    NULL,
    'AMMO',
    1
)
""")

utenti = {

    "Stazi boys": "XTRAVEL",
    "FC La urina": "CAPTAIN",
    "Inter-Pol": "SERGENTE",
    "Il Re del Fantacalcio": "KING",
    "Rivolta al RE": "PRINCIPE",
    "Borussia Baggins": "KDB",
    "SKIBIDI BRONDBY": "DOCTOR",
    "Faggiani Tattici Nucleari": "SISAL",
    "A.C. avanti chisto": "CIOCCA",
    "I Calypso Boys": "PRONGA",
    "Milancello": "MILANO",
    "Osasuca": "MLAUS"
}

for squadra, password in utenti.items():

    cursor.execute("""
    SELECT team_id
    FROM teams
    WHERE nome_squadra = ?
    """, (squadra,))

    risultato = cursor.fetchone()

    if risultato:

        cursor.execute("""
        INSERT INTO users (
            nome_account,
            team_id,
            password,
            is_admin
        )
        VALUES (?, ?, ?, 0)
        """, (
            squadra,
            risultato[0],
            password
        ))

conn.commit()
conn.close()

print("Utenti caricati")