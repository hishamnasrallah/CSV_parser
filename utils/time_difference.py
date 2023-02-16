from datetime import datetime


def time_difference_in_minutes(last_run):
    format1 = "%Y-%m-%dT%H:%M:%S.%f"
    format2 = "%Y-%m-%d %H:%M:%S.%f"
    try:
        time_now = datetime.strptime(str(datetime.now()), format2)
        print(time_now)
        last_run = datetime.strptime(str(last_run), format1)
        print(last_run)
        # last_run = datetime.strptime(last_run, format)
    except:
        time_now = datetime.strptime(str(datetime.now()), format2)
        print(time_now)
        last_run = datetime.strptime(str(last_run), format2)
        print(last_run)
        # last_run = datetime.strptime(last_run, format)
    diff = time_now - last_run
    diff_minutes = diff.total_seconds() / 60
    return diff_minutes


# print(time_difference_in_minutes("2023-01-25 11:47:17.376216"))