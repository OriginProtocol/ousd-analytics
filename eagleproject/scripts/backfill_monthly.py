import datetime
from django.conf import settings
from core.blockchain.harvest.transaction_history import create_time_interval_report_for_previous_month

def run():
    if not settings.ENABLE_REPORTS:
        print("Reports disabled on this instance")
        return

    year = datetime.datetime.now().year
    month = int(datetime.datetime.now().strftime("%m")) - 1
    while year > 2021 or (year == 2021 and month >= 5):
      create_time_interval_report_for_previous_month(
          year, month, False
      )
      month = 12 if month == 1 else month - 1
      year = year - 1 if month == 1 else year
