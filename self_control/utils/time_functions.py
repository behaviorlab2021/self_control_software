from datetime import datetime
import time

format_for_filename = '%Y.%m.%d_%H.%M.%S'
format_for_record = '%Y.%m.%d_%H.%M.%S'

def get_time_now():
    return datetime.now()


def get_time_dif(start_time):
    return datetime.now() - start_time

def get_timestamp_for_filename():
    now = datetime.now()
    timestamp = now.strftime(format_for_filename)
    return timestamp

def get_timestamp_for_record():
    now = datetime.now()
    timestamp = now.strftime(format_for_record)
    return timestamp

def get_timestamp_original():
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    return timestamp