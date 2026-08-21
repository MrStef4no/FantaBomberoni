from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ROME_TZ = ZoneInfo("Europe/Rome")

def utc_to_local(ts):
    if not ts:
        return ""

    utc_dt = datetime.fromisoformat(ts).replace(
        tzinfo=timezone.utc
    )

    return utc_dt.astimezone(ROME_TZ)