from django.conf import settings
from core.blockchain.harvest.transaction_history import create_time_interval_report_for_previous_week

def run():
    if not settings.ENABLE_REPORTS:
        print("Reports disabled on this instance")
        return

    create_time_interval_report_for_previous_week(
        None, False
    )
