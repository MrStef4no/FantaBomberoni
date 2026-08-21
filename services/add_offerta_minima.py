import sqlite3

conn = sqlite3.connect("database/fantalega.db")

cursor = conn.cursor()

try:

    cursor.execute("""
    ALTER TABLE sealed_rounds
    ADD COLUMN offerta_minima REAL
    """)

    conn.commit()

    print("Colonna offerta_minima aggiunta")

except Exception as e:

    print(e)

conn.close()