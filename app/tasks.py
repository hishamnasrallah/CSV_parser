
from celery_config.celery_utils import create_celery
from utils.csv_helpers import CSVHelper
from utils.time_difference import time_difference_in_minutes

celery = create_celery()


@celery.task(name='add new file process task')
def add_tasks(file_id, file_path, file_name, frequency, company_id, last_run):
    task_id = celery.current_task.request.id
    print(celery.AsyncResult.task_id)

    print(task_id)
    """

    :param file_id: the row id for the mapper configuration
    :param file_path: file path to using it in the celery function
    :param file_name: file name to use it as prefix name for all files in the real path
    :param frequency: the frequency in minutes
    :param company_id: company id from the core application, and it will be in the token
    :param last_run: when this configuration ran before
    :return: after checking the time difference between system time and the last run.
    if it greater than the frequency the function wil run.
    """
    time_diff_minutes = 0

    print(file_name)
    if last_run:
        time_diff_minutes = time_difference_in_minutes(last_run)
        if time_diff_minutes < frequency:
            print(time_diff_minutes)
        # else:
        #     print(frequency)
            return f"FILE: '{file_name}' need more time to send to celery"


    if time_diff_minutes > frequency or not last_run:
        csv_helper = CSVHelper(task_id=task_id, company_id=company_id, file_id=file_id, file_name=file_name, file_path=file_path)
        x = csv_helper.main()
        if x == "No files":
            return f"NO NEW FILE with prefix: '{file_name}'"
        print("mapped_data  : ", x)

        return f"FILE: '{file_name}' sent to celery"
