import sqlite3
from services.time_utils import now_rome

DB_PATH = "database/fantalega.db"


def get_market_override():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT setting_value
    FROM system_settings
    WHERE setting_key = 'MARKET_OVERRIDE'
    """)

    valore = cursor.fetchone()[0]

    conn.close()

    return valore

def get_phase_override():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT setting_value
    FROM system_settings
    WHERE setting_key = 'MARKET_PHASE_OVERRIDE'
    """)

    riga = cursor.fetchone()

    if riga is None:

        conn.close()

        return "AUTO"

    valore = riga[0]

    conn.close()

    return valore

def get_market_phase():
    #return "APERTURA_BUSTE"
    
    phase_override = get_phase_override()

    if phase_override != "AUTO":
        return phase_override
    
    override = get_market_override()

    if override == "CHIUSO":
        return "CHIUSO"

    if override == "APERTO":
        return "CHIAMATA"

    now = now_rome()

    giorno = now.weekday()
    ora = now.hour
    minuto = now.minute

    minuti = ora * 60 + minuto

    # Martedì
    if giorno == 1:
        return "CHIAMATA"

    # Mercoledì
    if giorno == 2:
        return "CHIAMATA"

    # Giovedì
    if giorno == 3:

        if minuti < 19 * 60:
            return "CHIAMATA"

        return "RILANCIO"

    # Venerdì
    if giorno == 4:

        if minuti < 12 * 60:
            return "RILANCIO"

        if minuti < 17 * 60:
            return "BUSTE"

        return "APERTURA_BUSTE"

    return "CHIUSO"