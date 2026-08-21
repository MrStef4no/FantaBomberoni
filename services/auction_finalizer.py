import sqlite3

from services.audit_utils import log_event

DB_PATH = "database/fantalega.db"


def finalize_auction(
    conn,
    auction_id,
    risultato
):

    cursor = conn.cursor()

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

    if risultato["tipo"] not in [
        "LEADER_PUBBLICO",
        "VINCITORE"
    ]:
        return False

    cursor.execute("""
    SELECT nome_squadra
    FROM teams
    WHERE team_id = ?
    """, (
        risultato["team_id"],
    ))

    nome_squadra = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM market_results
    WHERE auction_id = ?
    """, (
        auction_id,
    ))

    gia_registrata = cursor.fetchone()[0]

    if gia_registrata > 0:
        return True

    cursor.execute("""
    SELECT player_id
    FROM auctions
    WHERE auction_id = ?
    """, (
        auction_id,
    ))

    player_id = cursor.fetchone()[0]

    cursor.execute("""
    SELECT session_id
    FROM market_sessions
    WHERE stato = 'APERTA'
    LIMIT 1
    """)

    sessione = cursor.fetchone()

    if sessione is None:
        return False

    session_id = sessione[0]

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
        ?
    )
    """, (
        auction_id,
        player_id,
        risultato["team_id"],
        risultato["offerta"],
        session_id
    ))

    cursor.execute("""
    UPDATE auctions
    SET stato = 'CHIUSA'
    WHERE auction_id = ?
    """, (
        auction_id,
    ))

    conn.commit()

    log_event(
        conn,
        nome_squadra,
        "AGGIUDICAZIONE",
        f"{nome_giocatore} - {risultato['offerta']:.2f} FM"
    )

    return True