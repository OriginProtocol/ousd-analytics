from django.conf import settings

def gtm(request):
    return { 'GOOGLE_TAG_ID': settings.GOOGLE_TAG_ID }