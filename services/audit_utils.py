import sqlite3

def log_event(
    conn,
    squadra,
    tipo_evento,
    dettaglio
):

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO audit_log (
        data_evento,
        squadra,
        tipo_evento,
        dettaglio
    )
    VALUES (
        datetime('now'),
        ?,
        ?,
        ?
    )
    """, (
        squadra,
        tipo_evento,
        dettaglio
    ))

    conn.commit()
