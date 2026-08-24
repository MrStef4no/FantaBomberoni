import sqlite3

DB_PATH = "database/fantalega.db"

def get_last_notified_phase():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT setting_value
    FROM system_settings
    WHERE setting_key = 'LAST_NOTIFIED_PHASE'
    """)

    value = cursor.fetchone()[0]
    conn.close()

    return value


def set_last_notified_phase(phase):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE system_settings
    SET setting_value = ?
    WHERE setting_key = 'LAST_NOTIFIED_PHASE'
    """, (phase,))

    conn.commit()
    conn.close()