def chunks(list, chunk_size):
	for i in range(0, len(list), chunk_size):
	    yield list[i:i + chunk_size]

def datetime_to_start_day_utc(date):
	return datetime(date.year, date.month, date.day).replace(
    tzinfo=timezone.utc
  )