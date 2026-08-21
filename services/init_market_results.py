import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS market_results (

    result_id INTEGER PRIMARY KEY AUTOINCREMENT,

    auction_id INTEGER,

    player_id_acquistato INTEGER,

    team_id_vincitore INTEGER,

    prezzo_acquisto REAL,

    player_id_ceduto INTEGER,

    data_aggiudicazione TEXT
)
""")

conn.commit()

conn.close()

print("Tabella market_results creata")