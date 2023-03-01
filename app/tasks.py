
from celery_config.celery_utils import create_celery
from utils.csv_helpers import CSVHelper
from utils.time_difference import time_difference_in_minutes

celery = create_celery()


@celery.task(name='add new file process task')
def add_tasks(file_id, file_path, file_name, frequency, process_id, company_id, last_run):
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

    if last_run:
        time_diff_minutes = time_difference_in_minutes(last_run)
        if time_diff_minutes < frequency:
            return f"FILE: '{file_name}' need MORE TIME to send to celery"


    if time_diff_minutes > frequency or not last_run:
        csv_helper = CSVHelper(task_id=task_id, company_id=company_id, file_id=file_id, file_name=file_name,
                               file_path=file_path, process_id=process_id)
        x = csv_helper.main()
        if x == "No files":
            return f"NO NEW file with prefix: '{file_name}'"


        return f"FILE: '{file_name}' SENT to celery \n \n \n \n " + f"  {str(x)}"


