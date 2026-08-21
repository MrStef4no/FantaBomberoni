import sqlite3

# Creazione/apertura database
conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

# =========================
# TEAMS
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_squadra TEXT NOT NULL,
    manager TEXT NOT NULL,
    budget_residuo REAL NOT NULL,
    fase_cambi INTEGER NOT NULL,
    cambi_residui INTEGER NOT NULL
)
""")

# =========================
# PLAYERS
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    ruolo TEXT NOT NULL,
    ruolo_dettaglio TEXT,
    squadra_serie_a TEXT,
    quotazione REAL,
    fvm REAL,
    disponibile_mercato INTEGER DEFAULT 1
)
""")

# =========================
# ROSTERS
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS rosters (
    roster_id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    attivo INTEGER DEFAULT 1,
    bloccato_svincolo INTEGER DEFAULT 0,

    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
)
""")
# =========================
# SESSIONI MERCATO
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS market_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    descrizione TEXT,
    data_apertura TEXT,
    data_chiusura TEXT,
    stato TEXT
)
""")

# =========================
# ASTE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS auctions (
    auction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    player_id INTEGER,
    team_chiamante INTEGER,
    prezzo_partenza REAL,
    data_apertura TEXT,
    stato TEXT,

    FOREIGN KEY (session_id) REFERENCES market_sessions(session_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (team_chiamante) REFERENCES teams(team_id)
)
""")
# =========================
# OFFERTE PUBBLICHE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS public_bids (
    bid_id INTEGER PRIMARY KEY AUTOINCREMENT,
    auction_id INTEGER,
    team_id INTEGER,
    importo REAL,
    data_ora TEXT,

    FOREIGN KEY (auction_id) REFERENCES auctions(auction_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
)
""")
# =========================
# PARTECIPANTI ASTA
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS auction_participants (
    participant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    auction_id INTEGER,
    team_id INTEGER,
    ha_abbandonato INTEGER DEFAULT 0,

    FOREIGN KEY (auction_id) REFERENCES auctions(auction_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
)
""")
# =========================
# ROUND BUSTE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS sealed_rounds (
    round_id INTEGER PRIMARY KEY AUTOINCREMENT,
    auction_id INTEGER,
    round_number INTEGER,
    apertura TEXT,
    chiusura TEXT,
    stato TEXT
)
""")

# =========================
# OFFERTE SEGRETE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS sealed_bids (
    sealed_bid_id INTEGER PRIMARY KEY AUTOINCREMENT,
    round_id INTEGER,
    auction_id INTEGER,
    team_id INTEGER,
    importo REAL,
    data_ora TEXT
)
""")

# =========================
# PARTECIPANTI ROUND BUSTA
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS round_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    round_id INTEGER,
    team_id INTEGER
)
""")

# Salvataggio
conn.commit()

# Chiusura connessione
conn.close()

print("Database creato correttamente")