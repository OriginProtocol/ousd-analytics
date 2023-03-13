from django.conf import settings
from core.blockchain.harvest.transaction_history import send_weekly_email

def run():
    if not settings.ENABLE_REPORTS:
        print("Reports disabled on this instance")
        return

    send_weekly_email()
