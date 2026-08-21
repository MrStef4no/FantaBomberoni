import sqlite3

DB_PATH = "database/fantalega.db"


def get_current_round(auction_id):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        round_id,
        round_number
    FROM sealed_rounds
    WHERE auction_id = ?
      AND stato = 'APERTO'
    ORDER BY round_number DESC
    LIMIT 1
    """, (auction_id,))

    risultato = cursor.fetchone()

    conn.close()

    return risultato