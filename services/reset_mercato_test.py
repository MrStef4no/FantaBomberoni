import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

# Market results
cursor.execute("DELETE FROM market_results")

# Spareggi
cursor.execute("DELETE FROM round_participants")
cursor.execute("DELETE FROM sealed_bids")
cursor.execute("DELETE FROM sealed_rounds")

# Aste
cursor.execute("DELETE FROM auction_participants")
cursor.execute("DELETE FROM public_bids")
cursor.execute("DELETE FROM auctions")

# Reset autoincrement
cursor.execute("""
DELETE FROM sqlite_sequence
WHERE name IN (
    'market_results',
    'round_participants',
    'sealed_bids',
    'sealed_rounds',
    'auction_participants',
    'public_bids',
    'auctions'
)
""")

conn.commit()

print("Mercato di test azzerato")

conn.close()