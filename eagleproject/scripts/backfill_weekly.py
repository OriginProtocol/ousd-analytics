import datetime
from django.conf import settings
from core.blockchain.harvest.transaction_history import create_time_interval_report_for_previous_week

def run():
    if not settings.ENABLE_REPORTS:
        print("Reports disabled on this instance")
        return

    year = datetime.datetime.now().year
    week = int(datetime.datetime.now().strftime("%W")) - 1
    while year > 2021 or (year == 2021 and week >= 37):
      create_time_interval_report_for_previous_week(
          year, week, False
      )
      week = 51 if week == 0 else week - 1
      year = year - 1 if week == 0 else year
