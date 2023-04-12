import os
from time import sleep

import requests
from app.api.models import Parser, MapperTask, CeleryTaskStatus, Profile, MapperProfile, Status, \
    FileHistory, FileHistoryFailedRows
from app.api.repositories.common import CRUD
from app.api.repositories.csv import update_file_history_rows_number_based_on_status, create_failed_row, \
    update_failed_row
from celery_config.celery_utils import create_celery
from utils.time_difference import time_difference_in_minutes
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi.encoders import jsonable_encoder
from celery.result import AsyncResult
# from contextlib import contextmanager
# from redis import Redis
# import time


# LOCK_EXPIRE = 60 # Lock expires in 10 minutes
#
# redis_client = Redis(host='localhost', port=6379, db=0)


celery = create_celery()
celery.conf.beat_schedule = {
    'check-csv-files-every-120-seconds': {
        'task': 'app.tasks.check_csv_files',
        'schedule': 60.0,
    #     # // TODO: after fixing the seessions issue it should be returned to be 900.0 nested of 15.0
    },
    'retry-every-120-seconds': {
        'task': 'app.tasks.retry_failures',
        'schedule': 300.0,
    },
}


@celery.task()
def check_csv_files():
    """
    Check CSV files configuration model and schedule tasks if necessary.
    """
    db = CRUD().db_conn()
    tasks = db.query(Parser).filter(Parser.is_active == True)
    for task in tasks:
        file_path = task.file_path
        file_name = task.file_name
        frequency = task.frequency.value
        company_id = task.company_id
        last_run = task.last_run
        file_id = task.id
        process_id = task.process_id

        history = db.query(FileHistory).filter(
            FileHistory.file_id == file_id,
            or_(FileHistory.history_status == Status.pending,
                FileHistory.history_status == Status.in_progress)
        ).first()
        if history:
            return f"THERE IS FILE STILL RUNNING {jsonable_encoder(history)}"

        add_tasks.delay(file_id=file_id, file_path=file_path, file_name=file_name, frequency=frequency,
                        process_id=process_id,
                        company_id=company_id, last_run=last_run)
    return "Checked all mappers"


@celery.task(name='add new file to task')
def add_tasks(file_id, file_path, file_name, frequency, process_id, company_id, last_run):
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
    from utils.csv_helpers import CSVHelper

    task_id = celery.current_task.request.id

    time_diff_minutes = 0

    if last_run:
        time_diff_minutes = time_difference_in_minutes(last_run)
        if time_diff_minutes < frequency:
            return f"FILE: '{file_name}' need MORE TIME to send to celery"

    if time_diff_minutes > frequency or not last_run:
        csv_helper = CSVHelper(task_id=task_id, company_id=company_id, file_id=file_id, file_name=file_name,
                               file_path=file_path, process_id=process_id)
        result = csv_helper.main()
        if result == "No files":
            final_result = f"NO NEW file with prefix: '{file_name}'  with this path '{file_path}'"
        else:
            final_result = f"FILE: '{result['file_name_as_received']}' SENT to celery \n \n \n \n " + f"  {result['core_response'][:2]}"
        return final_result


@celery.task(name="set_mapper_active")
def mapper_activate(mapper_id: int):
    task_id = celery.current_task.request.id

    db: Session = CRUD().db_conn()

    mapper = db.query(Parser).filter(Parser.id == mapper_id)
    mapper_obj = mapper.first()
    if not mapper_obj:
        return {"mapper_id": mapper_id, "status": "Not Exists"}
    mapper_task = db.query(MapperTask).filter(MapperTask.task_id == task_id)
    if not mapper_task:
        pass
    else:
        linked_profile = db.query(MapperProfile).filter(MapperProfile.mapper_id == mapper_id).first()
        if linked_profile:
            profile = db.query(Profile).filter(Profile.id == linked_profile.profile_id).first()
            if profile.is_deleted:
                return {"mapper": mapper_obj.file_name, "status": "Cant change status, profile is deleted."}
            if not mapper_obj.is_active and not profile.is_active:
                return {"mapper": mapper_obj.file_name, "status": "Cant change status, profile is inactive."}
            mapper_task_obj = mapper_task.first()
            mapper_task_status = mapper_task_obj.status
            if mapper_task_status != CeleryTaskStatus.revoked:
                mapper_obj.is_active = True
                db.commit()

                mapper_tasks = db.query(MapperTask).filter(MapperTask.company_id == mapper_obj.company_id,
                                                           MapperTask.task_name == "set_mapper_active",
                                                           MapperTask.file_id == mapper_obj.id,
                                                           MapperTask.status == CeleryTaskStatus.received)
                mapper_tasks.update({MapperTask.status: CeleryTaskStatus.success})
                db.commit()

            return {"mapper": mapper_obj.file_name, "status": "Activated"}
        else:
            return {"mapper": mapper_obj.file_name, "status": "Cant change status, no profile linked."}


@celery.task()
def retry_failures():
    db = CRUD().db_conn()
    failed_rows = db.query(FileHistoryFailedRows).filter(FileHistoryFailedRows.number_of_reties <= 5).all()
    if not failed_rows:
        return "no failures with less 5 retries exist"
    for failed_row in failed_rows:
        original_file_history = db.query(FileHistory).filter(
            FileHistory.id == failed_row.history_id).first()
        parser = db.query(Parser).filter(
            Parser.id == original_file_history.file_id).first()
        if failed_row.task_id is not None:
            task = AsyncResult(failed_row.task_id, app=celery)
            if task.state in ['FAILURE', 'SUCCESS']:
                    send_collected_data.delay(parser.company_id, parser.process_id,
                                              failed_row.row_number, failed_row.history_id, failed_row.row_data,
                                              failed_row.file_id, True, failed_row.id)
        else:
                send_collected_data.delay(parser.company_id, parser.process_id,
                                          failed_row.row_number, failed_row.history_id, failed_row.row_data,
                                          failed_row.file_id, True, failed_row.id)
    return "Start retry failures"


@celery.task(name='send row')
def send_collected_data(company_id, process_id, row_number, history_id, data, file_id, is_retry=False,
                        row_history_id=None):

    task_id = celery.current_task.request.id
    host = os.environ.get('PRIVATE_CORE_ENDPOINT')
    headers = {
        "Host": "parser:8000"
    }
    url = f"{host}/api/v2/process/{process_id}/comapny/{company_id}/active_process/submit"
    try:
        response = requests.request("POST", url, headers=headers, data=data)
        db = CRUD().db_conn()

        if response.status_code == 201:
            status = Status.success
            update_failed_row(history_id=history_id, row_history_id=row_history_id, status=status, task_id=task_id,
                              db=db)
        else:
            status = Status.failed
            if not is_retry:
                row_history = db.query(FileHistoryFailedRows).filter(
                    FileHistoryFailedRows.id == row_history_id).first()
                if row_history.number_of_reties <= 5:
                    create_failed_row(history_id=history_id, file_id=file_id, row_number=row_number, row_data=data,
                                      task_id=task_id)
                    update_file_history_rows_number_based_on_status(history_id, status, db)
            else:
                update_failed_row(history_id=history_id, row_history_id=row_history_id, status=status, task_id=task_id,
                                  db=db)

    except:
        status = Status.failed
        db = CRUD().db_conn()
        if not is_retry:
            create_failed_row(history_id=history_id, file_id=file_id, row_number=row_number, row_data=data,
                              task_id=task_id)
            update_file_history_rows_number_based_on_status(history_id, status, db)
        else:
            update_failed_row(history_id=history_id, row_history_id=row_history_id, status=status, task_id=task_id,
                              db=db)
        response = "connection error"
    return {"core_response": str(response)}

