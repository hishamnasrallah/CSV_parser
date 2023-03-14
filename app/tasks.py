from app.api.models import ProcessConfig
from app.api.repositories.common import CRUD
from celery_config.celery_utils import create_celery
from utils.csv_helpers import CSVHelper
from utils.time_difference import time_difference_in_minutes
from sqlalchemy.orm import Session

celery = create_celery()
celery.conf.beat_schedule = {
    'check-csv-files-every-30-seconds': {
        'task': 'app.tasks.check_csv_files',
        'schedule': 120.0,
    },
}


@celery.task
def check_csv_files():
    """
    Check CSV files configuration model and schedule tasks if necessary.
    """
    db = CRUD().db_conn()
    tasks = db.query(ProcessConfig).filter(ProcessConfig.is_active==True)
    for task in tasks:
        file_path = task.file_path
        file_name = task.file_name
        frequency = task.frequency.value
        company_id = task.company_id
        last_run = task.last_run
        file_id = task.id
        process_id = task.process_id
        add_tasks.delay(file_id=file_id, file_path=file_path, file_name=file_name, frequency=frequency,
                        process_id=process_id,
                        company_id=company_id, last_run=last_run)
    return "Checked all mappers"


@celery.task(name='add new file process task 1111')
def add_tasks(file_id, file_path, file_name, frequency, process_id, company_id, last_run):
    task_id = celery.current_task.request.id

    """

    :param file_id: the row id for the mapper configuration
    :param file_path: file path to using it in the celery_config function
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
            return f"{x} NO NEW file with prefix: '{file_name}'  with this path '{file_path}'"

        return f"{x} FILE: '{file_name}' SENT to celery \n \n \n \n " + f"  {str(x)}"


@celery.task(name="set_mapper_active")
def mapper_activate(mapper_id: int):
    db: Session = CRUD().db_conn()

    mapper = db.query(ProcessConfig).filter(ProcessConfig.id == mapper_id)
    mapper_obj = mapper.first()
    if not mapper_obj:
        return {"mapper_id": mapper_id, "status": "Not Exists"}
    mapper_obj.is_active = True
    db.commit()
    return {"mapper": mapper_obj.file_name, "status": "Activated"}

