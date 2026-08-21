import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

try:

    cursor.execute("""
    ALTER TABLE market_results
    ADD COLUMN session_id INTEGER
    """)

    conn.commit()

    print("Colonna session_id aggiunta")

except Exception as e:

    print(e)

conn.close()