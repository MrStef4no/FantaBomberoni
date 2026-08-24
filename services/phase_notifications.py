from services.market_status import get_market_phase
from services.market_notifications import (
    get_last_notified_phase,
    set_last_notified_phase
)
from services.telegram_utils import send_telegram_message


def check_phase_notifications():

    current_phase = get_market_phase()
    last_phase = get_last_notified_phase()

    if current_phase == last_phase:
        return

    if current_phase == "CHIAMATA":

        send_telegram_message(
            "🟢 MERCATO APERTO\n"
            "✅ Inizio fase CHIAMATA\n"
            "⚽ Chiamate e rilanci consentiti"
        )

    elif current_phase == "RILANCIO":

        send_telegram_message(
            "🟡 FASE RILANCIO\n"
            "🚫 Chiamate chiuse\n"
            "⚠️ Da questo momento sono consentiti solo rilanci"
        )

    elif current_phase == "BUSTE":

        send_telegram_message(
            "🔵 FASE BUSTE CHIUSE\n"
            "📝 Inserimento buste aperto"
        )
        
    set_last_notified_phase(current_phase)
