from datetime import datetime
from zoneinfo import ZoneInfo

ROME = ZoneInfo("Europe/Rome")

def now_rome():
    return datetime.now(ROME)