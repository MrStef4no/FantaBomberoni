from services.time_utils import now_rome


def get_market_phase():

    now = now_rome()

    weekday = now.weekday()

    ora = now.hour
    minuto = now.minute

    # Martedì
    if weekday == 1:
        return "CHIAMATA"

    # Mercoledì
    if weekday == 2:
        return "CHIAMATA"

    # Giovedì
    if weekday == 3:

        if ora < 19:
            return "CHIAMATA"

        return "RILANCIO"

    # Venerdì
    if weekday == 4:

        if ora < 12:
            return "RILANCIO"

        if ora < 17:
            return "BUSTA_CHIUSA"

        return "CHIUSO"

    return "CHIUSO"