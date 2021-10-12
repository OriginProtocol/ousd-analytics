def chunks(list, chunk_size):
	for i in range(0, len(list), chunk_size):
	    yield list[i:i + chunk_size]