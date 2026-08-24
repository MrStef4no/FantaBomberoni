import sqlite3
from services.sealed_bid_utils import analyze_sealed_bids
from services.auction_finalizer import finalize_auction

DB_PATH = "database/fantalega.db"


def close_single_participant_auctions():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT auction_id
    FROM auctions
    WHERE stato = 'APERTA'
    """)

    aste = cursor.fetchall()

    aggiudicazioni = []
    aste_alle_buste = 0

    for asta in aste:

        auction_id = asta[0]

        cursor.execute("""
        SELECT COUNT(*)
        FROM auction_participants
        WHERE auction_id = ?
        AND ha_abbandonato = 0
        """, (auction_id,))

        partecipanti_attivi = cursor.fetchone()[0]

        if partecipanti_attivi != 1:
            aste_alle_buste += 1
            continue

        cursor.execute("""
        SELECT
            team_id,
            importo
        FROM public_bids
        WHERE auction_id = ?
        ORDER BY importo DESC, data_ora ASC
        LIMIT 1
        """, (auction_id,))

        leader = cursor.fetchone()

        if leader is None:
            continue

        team_id_vincitore = leader[0]
        prezzo = leader[1]

        cursor.execute("""
        SELECT player_id
        FROM auctions
        WHERE auction_id = ?
        """, (auction_id,))

        player_id = cursor.fetchone()[0]

        cursor.execute("""
        INSERT INTO market_results (
            auction_id,
            player_id_acquistato,
            team_id_vincitore,
            prezzo_acquisto,
            player_id_ceduto,
            data_aggiudicazione,
            session_id
        )
        VALUES (
            ?,
            ?,
            ?,
            ?,
            NULL,
            datetime('now'),
            (
                SELECT session_id
                FROM market_sessions
                WHERE stato = 'APERTA'
                LIMIT 1
            )
        )
        """, (
            auction_id,
            player_id,
            team_id_vincitore,
            prezzo
        ))

        cursor.execute("""
        SELECT nome
        FROM players
        WHERE player_id = ?
        """, (player_id,))

        nome_giocatore = cursor.fetchone()[0]

        cursor.execute("""
        SELECT nome_squadra
        FROM teams
        WHERE team_id = ?
        """, (team_id_vincitore,))

        nome_squadra = cursor.fetchone()[0]

        aggiudicazioni.append(
            f"⚽ {nome_giocatore}\n"
            f"👤 {nome_squadra} | 💰 {prezzo:.2f} FM"
        )

        cursor.execute("""
        UPDATE auctions
        SET stato = 'CHIUSA'
        WHERE auction_id = ?
        """, (auction_id,))

    conn.commit()

    if aggiudicazioni:

        testo_aggiudicazioni = "\n\n".join(
            aggiudicazioni
        )

        send_telegram_message(
            "🔵 FASE BUSTE CHIUSE\n\n"
            "🏆 AGGIUDICAZIONI DIRETTE\n\n"
            f"{testo_aggiudicazioni}\n\n"
            f"⚖️ {aste_alle_buste} aste proseguono alle buste chiuse"
        )

    conn.close()

def process_open_auctions():
    send_telegram_message("DEBUG - process_open_auctions eseguita")
    
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT auction_id
    FROM auctions
    WHERE stato = 'APERTA'
    """)

    risultati = []
    spareggi = 0    
    max_round_aperto = 1

    aste = cursor.fetchall()

    for asta in aste:

        auction_id = asta[0]

        risultato = analyze_sealed_bids(
            auction_id
        )

        if risultato["tipo"] in [
            "LEADER_PUBBLICO",
            "VINCITORE"
        ]:

            if finalize_auction(
                conn,
                auction_id,
                risultato
            ):

                cursor.execute("""
                SELECT nome
                FROM players
                WHERE player_id = (
                    SELECT player_id
                    FROM auctions
                    WHERE auction_id = ?
                )
                """, (auction_id,))

                nome_giocatore = cursor.fetchone()[0]

                cursor.execute("""
                SELECT nome_squadra
                FROM teams
                WHERE team_id = ?
                """, (
                    risultato["team_id"],
                ))

                nome_squadra = cursor.fetchone()[0]

                risultati.append(
                    f"⚽ {nome_giocatore}\n"
                    f"👤 {nome_squadra} | 💰 {risultato['offerta']:.2f} FM"
                )

        elif risultato["tipo"] == "PARITA":

            spareggi += 1

            cursor.execute("""
            SELECT MAX(round_number)
            FROM sealed_rounds
            WHERE auction_id = ?
            """, (
                auction_id,
            ))

            ultimo_round = cursor.fetchone()[0]

            if ultimo_round is None:
                ultimo_round = 1

            nuovo_round = ultimo_round + 1
   
            max_round_aperto = max(
                max_round_aperto,
                nuovo_round
            )

            cursor.execute("""
            UPDATE sealed_rounds
            SET stato = 'CHIUSO'
            WHERE auction_id = ?
            AND stato = 'APERTO'
            """, (
                auction_id,
            ))

            cursor.execute("""
            INSERT INTO sealed_rounds (
                auction_id,
                round_number,
                apertura,
                chiusura,
                stato,
                offerta_minima
            )
            VALUES (
                ?,
                ?,
                datetime('now'),
                datetime('now'),
                'APERTO',
                ?
            )
            """, (
                auction_id,
                nuovo_round,
                risultato["offerta"] + 0.50
            ))

            round_id = cursor.lastrowid

            for team_id in risultato["team_ids"]:

                cursor.execute("""
                INSERT INTO round_participants (
                    round_id,
                    team_id
                )
                VALUES (?, ?)
                """, (
                    round_id,
                    team_id
                ))

    conn.commit()

    if risultati or spareggi > 0:

        messaggio = (
            f"🟣 APERTURA BUSTE - ROUND {max_round_aperto}\n"
            "🏆 RISULTATI\n"
        )

        if risultati:   
            messaggio += "\n" + "\n".join(risultati)

        from services.time_utils import now_rome
        from datetime import timedelta

        ora_attuale = now_rome()

        if ora_attuale.minute < 30:
            scadenza = ora_attuale.replace(
                minute=30,
                second=0,
                microsecond=0
            )
        else:
            scadenza = (
                ora_attuale.replace(
                    minute=0,
                    second=0,
                    microsecond=0
                )
                + timedelta(hours=1)
            )

        scadenza = scadenza.strftime("%H:%M")

        if spareggi > 0:
            messaggio += (
                f"\n⚖️ Aperto nuovo round per {spareggi} aste entro le ore {scadenza}"
            )

        send_telegram_message(messaggio)

    conn.close()