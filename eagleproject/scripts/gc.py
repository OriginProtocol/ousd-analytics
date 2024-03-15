from datetime import datetime, timedelta

from core.logging import get_logger
from notify.models import EventSeen

log = get_logger(__name__)

def run():
    """ General garbage collection tasks """

    # event_seen is time sensitive and old entries are irrelevant
    try:
        EventSeen.objects.filter(
            last_seen__lt=datetime.utcnow() - timedelta(minutes=59)
        ).delete()
    except Exception:
        log.exception(
            "Exception occurred trying to do event garbage collection"
        )
