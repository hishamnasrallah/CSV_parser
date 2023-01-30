
from celery_config.celery_utils import create_celery
from utils.csv_helpers import CSVHelper
from utils.time_difference import time_difference_in_minutes
import time

celery = create_celery()


@celery.task(name='add new file process task')
def add_tasks(file_id, file_path, file_name, frequency, company_id, last_run):

    time_diff_minutes = 0
    if last_run:
        time_diff_minutes = time_difference_in_minutes(last_run)
        print(time_diff_minutes)
    # else:
    #     print(frequency)

    if time_diff_minutes > frequency or not last_run:
        csv_helper = CSVHelper(company_id=company_id, file_id=file_id, file_name=file_name, file_path=file_path)
        x = csv_helper.main()
        print("mapped_data  : ", x)

    return f"FILE: '{file_name}' sent to celery"
