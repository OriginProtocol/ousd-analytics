from django.http import HttpResponse

from notify.main import run_all


def run_triggers(request):
    run_all()
    return HttpResponse("ok")
