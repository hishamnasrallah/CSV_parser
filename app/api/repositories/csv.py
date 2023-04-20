import os
import traceback
from datetime import datetime, timedelta
import logging
import pytz
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from app.api.models import FileHistory, Parser, ProcessMapField, MapperTask, \
    CeleryTaskStatus, \
    MapperProfile, Profile, Status, FileHistoryFailedRows, \
    FileReceiveHistoryDetail
from app.api.repositories.common import CRUD
from app.brokers.decapolis_core import CoreApplicationBroker
from core.exceptions.csv import CSVConfigDoesNotExist, \
    FailedCreateNewFileTaskConfig, FailedToUpdateFileTaskConfig, \
    CSVConfigMapperFieldsDoesNotExist, CantChangeStatusNoProfileAssigned, \
    ProfileAlreadyDeleted, \
    CantChangeStatusProfileIsInactive, HistoryDoesNotExist, NoFailuresRows, \
    InvalidAuthentication
from sqlalchemy import orm
from utils.delete_specific_task import cancel_task
from fastapi.responses import StreamingResponse
import requests
from utils.generate_csv import generate_csv

logger = logging.getLogger()


def mappers_configs(token, db):
    """

    :param token: you have to pass token to this function to extract
        company_id from it
    :param db: is the database connection
    :return: it will return all mapping configurations for the specific company
    """

    configs = db.query(Parser).filter(
        Parser.company_id == token["company"]["id"]).all()
    return jsonable_encoder(configs)


def mapper_config_filter(token, name_contains, db):
    company_id = token["company"]["id"]
    mapper_config = db.query(Parser).filter(Parser.company_id == company_id,
                                            Parser.file_name.ilike(
                                                f'%{name_contains}%')
                                            ).all()
    return jsonable_encoder(mapper_config)


def mapper_details(token, parser_id, db):
    """

    :param token: you have to pass token to this function to extract
        company_id from it.
    :param parser_id: it should be the mapper configuration id
    :param db: is the database connection
    :return: the specific mapper configuration details with field mapping
    """

    mapper_config = db.query(Parser).filter(
        Parser.company_id == token["company"]["id"],
        Parser.id == parser_id).first()
    if not mapper_config:
        raise CSVConfigDoesNotExist

    mapper_fields = db.query(ProcessMapField).filter(
        ProcessMapField.file_id == parser_id).all()
    mapper_profile = db.query(MapperProfile).filter(
        MapperProfile.mapper_id == mapper_config.id
    ).first()
    if not mapper_profile:
        profile_id = None
    else:
        profile_id = mapper_profile.profile_id

    if not mapper_config:
        raise CSVConfigMapperFieldsDoesNotExist
    mapper_config = jsonable_encoder(mapper_config)
    mapper_config["mapper"] = jsonable_encoder(mapper_fields)
    mapper_config["profile_id"] = jsonable_encoder(profile_id)
    return jsonable_encoder(mapper_config)


def mappers_history(file_id, db):
    """

    :param file_id: mapper configuration id
    :param db: is the database connection
    :return: all history records for specific file
    """
    result = []
    file_histories = db.query(FileHistory).filter(
        FileHistory.file_id == file_id).all()
    for file_history in file_histories:
        file_history_detail = db.query(FileReceiveHistoryDetail).filter(
            FileReceiveHistoryDetail.history_id == file_history.id).first()
        file_history_dict = jsonable_encoder(file_history)
        file_history_dict["total_rows"] = file_history_detail.total_rows
        file_history_dict["total_success"] = file_history_detail.total_success
        file_history_dict["total_failure"] = file_history_detail.total_failure
        result.append(file_history_dict)
    return jsonable_encoder(result)


def file_history_detail(history_id, db, reties_count=None, row_task_id=None,
                        date=None):
    """

    :param history_id: parser history id
    :param db: is the database connection
    :return: all history records for specific file
    """
    file_history = db.query(FileHistory).filter(
        FileHistory.id == history_id)
    if not file_history.first():
        raise HistoryDoesNotExist
    file_history_obj = file_history.first()
    base_query = db.query(FileHistoryFailedRows).options(
        orm.defer('history_id')
    ).filter(
        FileHistoryFailedRows.history_id == file_history_obj.id)

    if reties_count:
        base_query = base_query.filter(
            FileHistoryFailedRows.number_of_reties == reties_count)
    if row_task_id:
        base_query = base_query.filter(
            FileHistoryFailedRows.task_id == row_task_id)
    if date:
        base_query = base_query.filter(
            FileHistoryFailedRows.created_at >= date,
            FileHistoryFailedRows.created_at < date + timedelta(days=1))

    print(base_query)
    return jsonable_encoder(base_query.all())


def export_failures_as_csv(history_id, db):
    """

    :param history_id: parser history id
    :param db: is the database connection
    :return: all history records for specific file
    """

    file_history = db.query(FileHistory).filter(
        FileHistory.id == history_id)
    if not file_history.first():
        raise HistoryDoesNotExist
    file_history_obj = file_history.first()
    failed_rows = db.query(FileHistoryFailedRows).filter(
        FileHistoryFailedRows.history_id == file_history_obj.id).all()
    try:
        column_names = list(failed_rows[0].as_dict().keys())
    except:
        raise NoFailuresRows
    filename = f"{file_history_obj.file_name_as_received}-failures.csv"
    rows = [[getattr(row, col.name) for col in
             FileHistoryFailedRows.__table__.columns] for row in failed_rows]

    response = StreamingResponse(generate_csv(column_names, rows), headers={
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Content-Type': 'text/csv'
    })

    return response


def delete_config(parser_id, token, db):
    """

    :param parser_id: mapper configuration id
    :param token: to extract company_id from it.
    :param db: the database connection
    :return: nothing
    """
    config = db.query(Parser).filter(Parser.id == parser_id,
                                     Parser.company_id == token["company"][
                                         "id"])
    if not config.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=CSVConfigDoesNotExist().message_key)
    else:
        config_obj = config.first()
        fields_mappers = db.query(ProcessMapField).filter(
            ProcessMapField.file_id == config_obj.id)
        parser_profile = db.query(MapperProfile).filter(
            MapperProfile.mapper_id == config_obj.id)
        parser_profile.delete(synchronize_session=False)
        fields_mappers.delete(synchronize_session=False)
        db.commit()

        config.delete(synchronize_session=False)
        db.commit()
        return 'deleted'


def get_file_mapper(file_id, db=CRUD().db_conn()):
    """

    :param file_id: mapper configuration id
    :param db: the database connection
    :return: all fields mapping for specific file
    """
    mapper = db.query(ProcessMapField).filter(
        ProcessMapField.file_id == file_id).all()
    return mapper


def get_file_history(file_id, file_name=None, db=CRUD().db_conn()):
    """

    :param file_id: mapper configuration id
    :param file_name: mapper configuration file name
    :param db: the database connection
    :return: history for specific file name as received
    """
    history = db.query(FileHistory).filter(FileHistory.file_id == file_id,
                                           FileHistory.file_name_as_received == file_name)
    return history


def get_company_processes(token, request):
    """

    :param token: to extract company_id from it.
    :param request: request as received to use it in the broker
    :return: the response from the broker that call an api from the core application
    """
    company_id = token["company"]["id"]
    broker = CoreApplicationBroker(request)
    response = broker.get_company_processes(company_id=company_id,
                                            response_message_key=200)
    jsonable_encoder(response)
    return jsonable_encoder(response)


def create_file_history(file_id, file_size, file_name_as_received, total_rows,
                        task_id="1"):
    history_rec = FileHistory(file_id=file_id, file_size_kb=file_size,
                              file_name_as_received=file_name_as_received,
                              task_id=task_id)
    history_rec = CRUD().add(history_rec)

    history_rec_details = FileReceiveHistoryDetail(history_id=history_rec.id,
                                                   file_id=file_id,
                                                   total_rows=total_rows,
                                                   total_success=0,
                                                   total_failure=0)
    CRUD().add(history_rec_details)
    return history_rec


def update_file_history_rows_number_based_on_status(history_id,
                                                    sending_row_status, db):
    history = db.query(FileHistory).filter(
        FileHistory.id == history_id).first()
    history_details = db.query(
        FileReceiveHistoryDetail).with_for_update().filter(
        FileReceiveHistoryDetail.history_id == history_id).first()

    if not history:
        raise HistoryDoesNotExist
    if sending_row_status == Status.success:
        history_details.total_success += 1
    else:
        history_details.total_failure += 1
    if history_details.total_rows == history_details.total_success:
        history.history_status = Status.success
    elif history_details.total_rows != history_details.total_success and \
            history_details.total_rows == history_details.total_success + history_details.total_failure:
        history.history_status = Status.failed
    else:
        history.history_status = Status.in_progress

    db.commit()


def create_failed_row(history_id, file_id, row_number, row_data, task_id,
                      error_msg):
    row_history_rec = FileHistoryFailedRows(history_id=history_id,
                                            file_id=file_id,
                                            row_number=row_number,
                                            number_of_reties=1,
                                            row_data=row_data,
                                            task_id=task_id,
                                            error_msg=error_msg)
    row_history_rec = CRUD().add(row_history_rec)
    return row_history_rec


def update_failed_row(history_id, row_history_id, sending_row_status, task_id,
                      is_retry, error_msg, db):
    history = db.query(FileHistory).with_for_update().filter(
        FileHistory.id == history_id).first()
    history_details = db.query(FileReceiveHistoryDetail).filter(
        FileReceiveHistoryDetail.id == history_id).first()
    row_history = db.query(FileHistoryFailedRows).filter(
        FileHistoryFailedRows.id == row_history_id).first()
    if sending_row_status == Status.failed:
        row_history.number_of_reties += 1
        row_history.task_id = task_id
        row_history.error_msg = error_msg
        db.commit()
    elif sending_row_status == Status.success:
        history_details.total_success += 1
        if is_retry:
            history_details.total_failure -= 1
            row_history.is_success = True
        if history_details.total_rows == history_details.total_success:
            history.history_status = Status.success
        elif history_details.total_rows == history_details.total_success + history_details.total_failure and \
                history_details.total_rows != history_details.total_success:
            history.history_status = Status.failed
        else:
            history.history_status = Status.in_progress
        db.query(FileHistoryFailedRows).filter(
            FileHistoryFailedRows.id == row_history_id).delete()
        db.commit()


def update_last_run(file_config_id, db=CRUD().db_conn()):
    config = db.query(Parser).filter(Parser.id == file_config_id)
    if not config.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=CSVConfigDoesNotExist().message_key)
    else:
        stored_data = jsonable_encoder(config.first())

        time_format = "%Y-%m-%d %H:%M:%S.%f"

        time_now = datetime.strptime(str(datetime.now()), time_format)

        stored_data["last_run"] = time_now

        config.update(stored_data)
        db.commit()
        return stored_data


def change_mapper_status(parser_id, token, db):
    company_id = token["company"]["id"]

    mapper_config_obj = db.query(Parser).filter(Parser.id == parser_id,
                                                Parser.company_id == company_id).first()

    if not mapper_config_obj:
        raise CSVConfigDoesNotExist
    linked_profile = db.query(MapperProfile).filter(
        MapperProfile.mapper_id == mapper_config_obj.id).first()
    if not linked_profile:
        raise CantChangeStatusNoProfileAssigned
    profile = db.query(Profile).filter(
        Profile.id == linked_profile.profile_id).first()
    if profile.is_deleted:
        raise ProfileAlreadyDeleted
    if not mapper_config_obj.is_active and not profile.is_active:
        raise CantChangeStatusProfileIsInactive

    if mapper_config_obj.is_active:
        mapper_config_obj.is_active = False
    elif not mapper_config_obj.is_active:
        mapper_config_obj.is_active = True
    else:
        mapper_config_obj.is_active = True
    db.commit()
    return jsonable_encoder(mapper_config_obj)


def update_config(request_body, parser_id, token, db):
    """

    :param db: db connection
    :param request_body: the data that sent to the api as json
    :param parser_id: related parser id
    :param token: to extract company_id from it
    :return: new configuration
    """
    from app.tasks import mapper_activate

    try:
        request_dict = request_body.dict()
        request_dict["company_id"] = token["company"]["id"]
        mapper = request_dict.pop("mapper", None)
        mapper_config = db.query(Parser).filter(Parser.id == parser_id)
        mapper_config_obj = mapper_config.first()
        if "set_active_at" not in request_dict.keys() or request_dict[
            "is_active"]:
            request_dict['set_active_at'] = None
        profile_id = request_dict.pop("profile_id", None)
        if not profile_id:
            request_dict["is_active"] = False
            request_dict["set_active_at"] = None
        else:
            mapper_profile_obj = db.query(MapperProfile).filter(
                MapperProfile.mapper_id == mapper_config_obj.id).first()
            if not mapper_profile_obj:
                link_parser_with_profile = MapperProfile(
                    mapper_id=mapper_config_obj.id, profile_id=profile_id)
                CRUD().add(link_parser_with_profile)
            else:
                mapper_profile_obj.profile_id = profile_id
                db.commit()
        for key, value in request_dict.items():
            setattr(mapper_config_obj, key, value)
        db.commit()
        if (not request_dict['set_active_at'] and not request_dict[
            "is_active"]) or request_dict["is_active"]:
            mapper_tasks = db.query(MapperTask).filter(
                MapperTask.company_id == int(request_dict["company_id"]),
                MapperTask.task_name == "set_mapper_active",
                MapperTask.file_id == mapper_config_obj.id,
                MapperTask.status == CeleryTaskStatus.received)
            task_id_list = [task.task_id for task in mapper_tasks]
            cancel_task(task_id_list)
            mapper_tasks.update({MapperTask.status: CeleryTaskStatus.revoked})
            db.commit()
        elif mapper_config_obj.set_active_at:
            task = mapper_activate.apply_async(args=(mapper_config_obj.id,),
                                               eta=mapper_config_obj.set_active_at.astimezone(
                                                   pytz.utc))
            mapper_task = MapperTask(
                company_id=int(request_dict["company_id"]), task_id=str(task),
                file_id=mapper_config_obj.id,
                task_name="set_mapper_active",
                status=CeleryTaskStatus.received)

            CRUD().add(mapper_task)
        response = jsonable_encoder(mapper_config.first())
        mapper_objs = db.query(ProcessMapField).filter(
            ProcessMapField.file_id == parser_id)
        mapper_objs.delete(synchronize_session=False)
        db.commit()
        mappers = []
        for item in mapper:
            map_rec = ProcessMapField(file_id=parser_id,
                                      field_name=item.field_name,
                                      map_field_name=item.map_field_name,
                                      is_ignored=item.is_ignored)
            stored_map_rec = CRUD().add(map_rec)
            mappers.append(jsonable_encoder(stored_map_rec))
        response["mapper"] = mappers
        return response
    except:
        raise FailedToUpdateFileTaskConfig


def create_config(request_body, token):
    """

    :param request_body: the data that sent to the api as json
    :param token: to extract company_id from it
    :return: new configuration
    """
    from app.tasks import mapper_activate

    request_dict = request_body.dict()
    request_dict["company_id"] = token["company"]["id"]
    try:
        mapper = request_dict.pop("mapper", None)
        profile_id = request_dict.pop("profile_id", None)
        if not profile_id:
            request_dict["is_active"] = False
        rec = Parser(**request_dict)
        file_config_rec = CRUD().add(rec)
        if profile_id:
            link_parser_with_profile = MapperProfile(
                mapper_id=file_config_rec.id, profile_id=profile_id)
            CRUD().add(link_parser_with_profile)
        if file_config_rec.set_active_at:
            mapper_activate.apply_async(args=(file_config_rec.id,),
                                        eta=file_config_rec.set_active_at.astimezone(
                                            pytz.utc))
        file_id = file_config_rec.id
        response = jsonable_encoder(file_config_rec)
        mappers = []
        for item in mapper:
            map_rec = ProcessMapField(file_id=file_id,
                                      field_name=item.field_name,
                                      map_field_name=item.map_field_name,
                                      is_ignored=item.is_ignored)
            stored_map_rec = CRUD().add(map_rec)
            mappers.append(jsonable_encoder(stored_map_rec))

        response["mapper"] = mappers

        return response
    except Exception as e:
        print(
            f" \n <====== Exception =====> : \n {str(traceback.format_exc())} \n <==== End Exception ===>  \n")
        print(str(e))
        raise FailedCreateNewFileTaskConfig


def execute_mapper(token, parser_id, db):
    from utils.csv_helpers import CSVHelper

    company_id = token["company"]["id"]
    mapper_config = db.query(Parser).filter(Parser.id == parser_id,
                                            Parser.company_id == company_id)

    if not mapper_config.first():
        raise CSVConfigMapperFieldsDoesNotExist

    mapper_config_obj = mapper_config.first()

    csv_helper = CSVHelper(task_id="Ran manual", company_id=company_id,
                           file_id=mapper_config_obj.id,
                           file_name=mapper_config_obj.file_name,
                           file_path=mapper_config_obj.file_path,
                           process_id=mapper_config_obj.process_id)
    x = csv_helper.main()
    if x == "No files":
        return f"{x} NO NEW file with prefix: '{mapper_config_obj.file_name}'" \
               f"  with this path '{mapper_config_obj.file_path}'"

    return f"{x} FILE: '{mapper_config_obj.file_name}' SENT to celery \n \n \n \n " + f"  {str(x)}"


def consume_failures(token, history_id, failures_ids, db):
    company_id = token["company"]["id"]

    file_history = db.query(FileHistory).filter(
        FileHistory.id == history_id)
    if not file_history.first():
        raise HistoryDoesNotExist
    file_history_obj = file_history.first()
    parser = db.query(Parser).filter(
        Parser.id == file_history_obj.file_id)
    if not parser.first():
        raise CSVConfigDoesNotExist
    parser_obj = parser.first()
    process_id = parser_obj.process_id
    if parser_obj.company_id != company_id:
        raise InvalidAuthentication

    failed_rows_base_query = db.query(FileHistoryFailedRows).filter(
        FileHistoryFailedRows.history_id == history_id)
    if len(failures_ids) > 0:
        failed_rows_base_query = failed_rows_base_query.filter(
            FileHistoryFailedRows.id.in_(failures_ids)).all()
    if not failed_rows_base_query:
        raise NoFailuresRows
    result = []
    for failed_row in failed_rows_base_query:
        host = os.environ.get('PRIVATE_CORE_ENDPOINT')
        headers = {
            "Host": "parser:8000"
        }
        url = f"{host}/api/v2/process/{process_id}/comapny/{company_id}/active_process/submit"
        try:
            # response = requests.Request()
            # response.status_code = 201
            # response.content = "success"

            response = requests.request("POST", url, headers=headers,
                                        data=failed_row.row_data)
            if response.status_code == 201:
                status = Status.success
                update_failed_row(history_id=history_id,
                                  row_history_id=failed_row.id,
                                  sending_row_status=status,
                                  task_id="Ran Manual",
                                  is_retry=True,
                                  error_msg=response.status_code,
                                  db=db)
                result.append({"row_numer": failed_row.row_number,
                               "row_data": failed_row.row_data,
                               "parser_id": failed_row.file_id,
                               "history_id": failed_row.history_id,
                               "core_response": response.content,
                               "status_code": 201})
            else:
                status = Status.failed
                update_failed_row(history_id=history_id,
                                  row_history_id=failed_row.id,
                                  sending_row_status=status,
                                  task_id="Ran Manual",
                                  is_retry=True,
                                  error_msg=response.status_code,
                                  db=db)
                result.append({"row_numer": failed_row.row_number,
                               "row_data": failed_row.row_data,
                               "parser_id": failed_row.file_id,
                               "history_id": failed_row.history_id,
                               "core_response": response.content,
                               "status_code": response.status_code})
        except Exception as e:

            status = Status.failed
            update_failed_row(history_id=history_id,
                              row_history_id=failed_row.id,
                              sending_row_status=status,
                              task_id="Ran Manual",
                              is_retry=True,
                              error_msg=(str(e)),
                              db=db)
            result.append({"row_numer": failed_row.row_number,
                           "row_data": failed_row.row_data,
                           "parser_id": failed_row.file_id,
                           "history_id": failed_row.history_id,
                           "core_response": str(e),
                           "status_code": 500})

    return jsonable_encoder(result)


def clone_mapper(token, parser_id, db):
    company_id = token["company"]["id"]
    mapper_config = db.query(Parser).filter(Parser.id == parser_id,
                                            Parser.company_id == company_id)
    if not mapper_config.first():
        raise CSVConfigDoesNotExist
    mapper_config_obj = mapper_config.first()
    rec = Parser(process_id=mapper_config_obj.process_id,
                 company_id=mapper_config_obj.company_id,
                 file_name=mapper_config_obj.file_name,
                 file_path=mapper_config_obj.file_path,
                 frequency=mapper_config_obj.frequency,
                 description=mapper_config_obj.description,
                 set_active_at=mapper_config_obj.set_active_at,
                 is_active=mapper_config_obj.is_active
                 )

    rec.file_name = f"[CLONE] - {rec.file_name}"
    rec.description = f"[CLONE] - {rec.description}"

    mapper_id = mapper_config_obj.id
    file_config_rec = CRUD().add(rec)
    mapper_profile = db.query(MapperProfile).filter(
        MapperProfile.mapper_id == parser_id)
    cloned_mapper_id = file_config_rec.id
    profile_id = None
    if mapper_profile.first():
        mapper_profile_obj = mapper_profile.first()
        mapper_profile_rec = MapperProfile(
            profile_id=mapper_profile_obj.profile_id,
            mapper_id=cloned_mapper_id)
        mapper_profile_rec = CRUD().add(mapper_profile_rec)
        profile_id = mapper_profile_rec.profile_id

    mapper_fields = db.query(ProcessMapField).filter(
        ProcessMapField.file_id == mapper_id).all()

    for field_mapper in mapper_fields:
        field_rec = ProcessMapField(file_id=file_config_rec.id,
                                    field_name=field_mapper.field_name,
                                    map_field_name=field_mapper.map_field_name,
                                    is_ignored=field_mapper.is_ignored
                                    )
        CRUD().add(field_rec)
    mapper_fields = db.query(ProcessMapField).filter(
        ProcessMapField.file_id == cloned_mapper_id).all()
    cloned_mapper_config = jsonable_encoder(rec)
    cloned_mapper_config["profile_id"] = profile_id
    cloned_mapper_config["mapper"] = jsonable_encoder(mapper_fields)
    return jsonable_encoder(cloned_mapper_config)
