import sqlite3

DB_PATH = "database/fantalega.db"


def get_leader(auction_id):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        pb.team_id,
        pb.importo
    FROM public_bids pb
    JOIN auction_participants ap
        ON pb.auction_id = ap.auction_id
       AND pb.team_id = ap.team_id
    WHERE pb.auction_id = ?
      AND ap.ha_abbandonato = 0
    ORDER BY pb.importo DESC,
             pb.bid_id DESC
    LIMIT 1
    """, (auction_id,))

    leader = cursor.fetchone()

    conn.close()

    return leader

def count_active_participants(auction_id):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM auction_participants
    WHERE auction_id = ?
      AND ha_abbandonato = 0
    """, (auction_id,))

    totale = cursor.fetchone()[0]

    conn.close()

    return totale


def get_leader_name(auction_id):

    leader = get_leader(auction_id)

    if not leader:
        return "Nessuno"

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT nome_squadra
    FROM teams
    WHERE team_id = ?
    """, (leader[0],))

    nome = cursor.fetchone()[0]

    conn.close()

    return nome