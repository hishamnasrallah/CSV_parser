from datetime import datetime


def time_difference_in_minutes(last_run):
    format1 = "%Y-%m-%dT%H:%M:%S.%f"
    format2 = "%Y-%m-%d %H:%M:%S.%f"
    try:
        time_now = datetime.strptime(str(datetime.now()), format2)
        last_run = datetime.strptime(str(last_run), format1)
    except:
        time_now = datetime.strptime(str(datetime.now()), format2)
        last_run = datetime.strptime(str(last_run), format2)
    diff = time_now - last_run
    diff_minutes = diff.total_seconds() / 60
    return diff_minutes
