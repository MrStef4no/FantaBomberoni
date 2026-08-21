import sqlite3

conn = sqlite3.connect("database/fantalega.db")
cursor = conn.cursor()

print("=== MARKET RESULTS ===")

cursor.execute("""
SELECT *
FROM market_results
ORDER BY result_id DESC
""")

for riga in cursor.fetchall():
    print(riga)

print("\n=== AUCTIONS ===")

cursor.execute("""
SELECT
    auction_id,
    stato
FROM auctions
ORDER BY auction_id DESC
""")

for riga in cursor.fetchall():
    print(riga)

conn.close()