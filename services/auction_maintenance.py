import sqlite3

DB_PATH = "database/fantalega.db"


def close_empty_auctions():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT auction_id
    FROM auctions
    WHERE stato = 'APERTA'
    """)

    aste = cursor.fetchall()

    for asta in aste:

        auction_id = asta[0]

        cursor.execute("""
        SELECT COUNT(*)
        FROM auction_participants
        WHERE auction_id = ?
          AND ha_abbandonato = 0
        """, (auction_id,))

        partecipanti = cursor.fetchone()[0]

        if partecipanti == 0:

            cursor.execute("""
            UPDATE auctions
            SET stato = 'ANNULLATA'
            WHERE auction_id = ?
            """, (auction_id,))

    conn.commit()
    conn.close()
