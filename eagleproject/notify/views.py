import sys
from datetime import datetime, timedelta
from django.http import HttpResponse

from notify.models import EventSeen
from notify.main import run_all


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
    except Exception as err:
        print(err, file=sys.stderr)

    return HttpResponse("ok")
