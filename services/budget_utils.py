import sqlite3
from services.auction_utils import get_leader

DB_PATH = "database/fantalega.db"


def budget_disponibile(nome_squadra):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    # recupero team_id
    cursor.execute("""
    SELECT team_id, budget_residuo
    FROM teams
    WHERE nome_squadra = ?
    """, (nome_squadra,))

    team_id, budget_residuo = cursor.fetchone()

    # recupero aste aperte
    cursor.execute("""
    SELECT auction_id
    FROM auctions
    WHERE stato = 'APERTA'
    """)

    aste = cursor.fetchall()

    budget_impegnato = 0

    for asta in aste:

        auction_id = asta[0]

        leader = get_leader(auction_id)

        if leader:

            leader_team_id = leader[0]
            leader_importo = leader[1]

            if leader_team_id == team_id:

                budget_impegnato += leader_importo

    conn.close()

    return round(
        budget_residuo - budget_impegnato,
        2
    )