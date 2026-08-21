import sqlite3

conn = sqlite3.connect(r"database/fantalega.db")

cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM players")

totale = cursor.fetchone()[0]

print(f"Totale giocatori: {totale}")

conn.close()