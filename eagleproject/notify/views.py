from datetime import datetime, timedelta
from django.http import HttpResponse

from core.logging import get_logger
from notify.models import EventSeen
from notify.main import run_all

log = get_logger(__name__)


def run_triggers(request):
    run_all()
    return HttpResponse("ok")


def gc(request):
    """ General garbage collection tasks """

    # event_seen is time sensitive and old entries are irrelevant
    try:
        EventSeen.objects.filter(
            last_seen__gt=datetime.utcnow() - timedelta(hours=2)
        ).delete()
    except Exception:
        log.exception(
            "Exception occurred trying to do event garbage collection"
        )

    return HttpResponse("ok")
