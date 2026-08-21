import sqlite3

DB_PATH = "database/fantalega.db"


def analyze_sealed_bids(auction_id):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    # -----------------------------
    # LEADER PUBBLICO
    # -----------------------------

    cursor.execute("""
    SELECT
        team_id,
        importo
    FROM public_bids
    WHERE auction_id = ?
    ORDER BY importo DESC,
             bid_id DESC
    LIMIT 1
    """, (auction_id,))

    leader_pubblico = cursor.fetchone()

    if not leader_pubblico:

        conn.close()

        return {
            "tipo": "NESSUN_LEADER"
        }

    leader_team_id = leader_pubblico[0]
    leader_importo = leader_pubblico[1]

    # -----------------------------
    # BUSTE PRESENTATE
    # -----------------------------

    cursor.execute("""
    SELECT
        round_id
    FROM sealed_rounds
    WHERE auction_id = ?
    AND stato = 'APERTO'
    ORDER BY round_number DESC
    LIMIT 1
    """, (auction_id,))

    round_corrente = cursor.fetchone()

    if round_corrente:

        round_id = round_corrente[0]

    else:

        round_id = 0

    cursor.execute("""
    SELECT
        team_id,
        importo
    FROM sealed_bids
    WHERE auction_id = ?
    AND round_id = ?
    ORDER BY importo DESC
    """, (
        auction_id,
        round_id
    ))

    buste = cursor.fetchall()
    print("LEADER PUBBLICO:", leader_team_id, leader_importo)
    print("BUSTE:", buste)
    conn.close()

    # -----------------------------
    # NESSUNA BUSTA
    # -----------------------------

    if len(buste) == 0:

        return {
            "tipo": "LEADER_PUBBLICO",
            "team_id": leader_team_id,
            "offerta": leader_importo
        }

    # -----------------------------
    # CASO SPECIALE:
    # SOLO IL LEADER HA PRESENTATO
    # UNA BUSTA

    if (
        len(buste) == 1
        and buste[0][0] == leader_team_id
    ):

        # Round 1
        if round_id == 0:

            return {
                "tipo": "LEADER_PUBBLICO",
                "team_id": leader_team_id,
                "offerta": leader_importo
            }

        # Spareggi (Round 2+)
        else:

            return {
                "tipo": "VINCITORE",
                "team_id": leader_team_id,
                "offerta": buste[0][1]
            }

    # -----------------------------
    # CONSIDERO SOLO LE BUSTE
    # CHE SUPERANO IL LEADER
    # PUBBLICO
    # -----------------------------

    superiori = [
        b
        for b in buste
        if b[1] > leader_importo
    ]
    print("SUPERIORI:", superiori)
    # -----------------------------
    # NESSUNO SUPERA IL LEADER
    # -----------------------------

    if len(superiori) == 0:

        return {
            "tipo": "LEADER_PUBBLICO",
            "team_id": leader_team_id,
            "offerta": leader_importo
        }

    # -----------------------------
    # MIGLIOR OFFERTA
    # -----------------------------

    miglior_offerta = superiori[0][1]

    pari = [
        b
        for b in superiori
        if b[1] == miglior_offerta
    ]
    print("PARI:", pari)
    # -----------------------------
    # VINCITORE UNICO
    # -----------------------------

    if len(pari) == 1:

        return {
            "tipo": "VINCITORE",
            "team_id": pari[0][0],
            "offerta": miglior_offerta
        }

    # -----------------------------
    # PARITA'
    # -----------------------------

    return {
        "tipo": "PARITA",
        "offerta": miglior_offerta,
        "team_ids": [p[0] for p in pari]
    }