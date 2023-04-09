import traceback
from datetime import datetime

import pytz
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from app.api.models import FileReceiveHistory, ProcessConfig, ProcessMapField, MapperTask, CeleryTaskStatus, \
    MapperProfile, Profile, Status
from app.api.repositories.common import CRUD
from app.brokers.decapolis_core import CoreApplicationBroker
from core.exceptions.csv import CSVConfigDoesNotExist, FailedCreateNewFileTaskConfig, FailedToUpdateFileTaskConfig, \
    CSVConfigMapperFieldsDoesNotExist, CantChangeStatusNoProfileAssigned, ProfileAlreadyDeleted, \
    CantChangeStatusProfileIsInactive
from utils.delete_specific_task import cancel_task


def mappers_configs(token, db):
    """

    :param token: you have to pass token to this function to extract company_id from it
    :param db: is the database connection
    :return: it will return all mapping configurations for the specific company
    """

    configs = db.query(ProcessConfig).filter(ProcessConfig.company_id == token["company"]["id"]).all()
    return jsonable_encoder(configs)


def mapper_config_filter(token, name_contains, db):
    company_id = token["company"]["id"]
    mapper_config = db.query(ProcessConfig).filter(ProcessConfig.company_id == company_id,
                                                   ProcessConfig.file_name.ilike(f'%{name_contains}%')
                                                   ).all()
    return jsonable_encoder(mapper_config)


def mapper_details(token, id, db):
    """

    :param token: you have to pass token to this function to extract company_id from it.
    :param id: it should be the mapper configuration id
    :param db: is the database connection
    :return: the specfic mapper configuration details with field mapping
    """

    mapper_config = db.query(ProcessConfig).filter(ProcessConfig.company_id == token["company"]["id"],
                                                   ProcessConfig.id == id).first()
    if not mapper_config:
        raise CSVConfigDoesNotExist

    mapper_fields = db.query(ProcessMapField).filter(ProcessMapField.file_id == id).all()
    profile = db.query(Profile).filter(
        Profile.company_id == token["company"]["id"],
        Profile.is_deleted == False
    ).first()
    if profile:
        profile_id = profile.id
    else:
        profile_id = None
    if not mapper_config:
        raise CSVConfigMapperFieldsDoesNotExist
    mapper_config = jsonable_encoder(mapper_config)
    mapper_config["mapper"] = jsonable_encoder(mapper_fields)
    mapper_config["profile_id"] = jsonable_encoder(profile_id)
    return jsonable_encoder(mapper_config)


def mappers_history(token, file_id, db):
    """

    :param file_id: mapper configuration id
    :param db: is the database connection
    :return: all history records for specific file
    """
    configs = db.query(FileReceiveHistory).filter(FileReceiveHistory.file_id == file_id).all()
    jsonable_encoder(configs)
    return jsonable_encoder(configs)


def delete_config(id, token, db):
    """

    :param id: mapper configuration id
    :param token: to extract company_id from it.
    :param db: the database connection
    :return: nothing
    """
    config = db.query(ProcessConfig).filter(ProcessConfig.id == id, ProcessConfig.company_id == token["company"]["id"])
    if not config.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=CSVConfigDoesNotExist().message_key)
    else:
        config_obj = config.first()
        fields_mappers = db.query(ProcessMapField).filter(ProcessMapField.file_id == config_obj.id)

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
    mapper = db.query(ProcessMapField).filter(ProcessMapField.file_id == file_id).all()
    return mapper


def get_file_history(file_id, file_name=None, db=CRUD().db_conn()):
    """

    :param file_id: mapper configuration id
    :param file_name: mapper configuration file name
    :param db: the database connection
    :return: history for specific file name as received
    """
    history = db.query(FileReceiveHistory).filter(FileReceiveHistory.file_id == file_id,
                                                  FileReceiveHistory.file_name_as_received == file_name)
    return history


def get_company_processes(token, request):
    """

    :param token: to extract company_id from it.
    :param request: request as received to use it in the broker
    :return: the response from the broker that call an api from the core application
    """
    company_id = token["company"]["id"]
    broker = CoreApplicationBroker(request)
    response = broker.get_company_processes(company_id=company_id, response_message_key=200)
    jsonable_encoder(response)
    return jsonable_encoder(response)


def create_file_history(file_id, file_size, file_name_as_received, total_rows, task_id="1"):
    history_rec = FileReceiveHistory(file_id=file_id, file_size_kb=file_size,
                                     file_name_as_received=file_name_as_received, total_rows=total_rows,
                                     total_success=0, total_failure=0, task_id=task_id)
    history_rec = CRUD().add(history_rec)
    return history_rec


def update_file_history_rows_number_based_on_status(id, status, db):
    history = db.query(FileReceiveHistory).filter(FileReceiveHistory.id == id).first()
    if not history:
        raise "batata"
    if status == Status.success:
        history.total_success += 1
    else:
        history.total_failure += 1
    db.commit()


def update_last_run(file_config_id, db=CRUD().db_conn()):
    config = db.query(ProcessConfig).filter(ProcessConfig.id == file_config_id)
    if not config.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=CSVConfigDoesNotExist().message_key)
    else:
        stored_data = jsonable_encoder(config.first())

        format = "%Y-%m-%d %H:%M:%S.%f"

        time_now = datetime.strptime(str(datetime.now()), format)

        stored_data["last_run"] = time_now

        config.update(stored_data)
        db.commit()
        return stored_data


def change_mapper_status(id, token, db):
    company_id = token["company"]["id"]

    mapper_config_obj = db.query(ProcessConfig).filter(ProcessConfig.id == id,
                                                       ProcessConfig.company_id == company_id).first()

    if not mapper_config_obj:
        raise CSVConfigDoesNotExist
    linked_profile = db.query(MapperProfile).filter(MapperProfile.mapper_id == mapper_config_obj.id).first()
    if not linked_profile:
        raise CantChangeStatusNoProfileAssigned
    profile = db.query(Profile).filter(Profile.id == linked_profile.profile_id).first()
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


def update_config(request_body, id, token, db):
    """

    :param request_body: the data that sent to the api as json
    :param token: to extract company_id from it
    :return: new configuration
    """
    from app.tasks import mapper_activate

    try:
        request_dict = request_body.dict()
        request_dict["company_id"] = token["company"]["id"]
        mapper = request_dict.pop("mapper", None)
        mapper_config = db.query(ProcessConfig).filter(ProcessConfig.id == id)
        mapper_config_obj = mapper_config.first()
        if "set_active_at" not in request_dict.keys() or request_dict["is_active"]:
            request_dict['set_active_at'] = None
        profile_id = request_dict.pop("profile_id", None)
        if not profile_id:
            request_dict["is_active"] = False
            request_dict["set_active_at"] = None
        else:
            mapper_profile_obj = db.query(MapperProfile).filter(MapperProfile.mapper_id == mapper_config_obj.id).first()
            if not mapper_profile_obj:
                link_parser_with_profile = MapperProfile(mapper_id=mapper_config_obj.id, profile_id=profile_id)
                link_parser_with_profile_rec = CRUD().add(link_parser_with_profile)
            else:
                mapper_profile_obj.profile_id = profile_id
                db.commit()
        for key, value in request_dict.items():
            setattr(mapper_config_obj, key, value)
        db.commit()
        if not request_dict['set_active_at'] and not request_dict["is_active"]:
            mapper_tasks = db.query(MapperTask).filter(MapperTask.company_id == int(request_dict["company_id"]),
                                                       MapperTask.task_name == "set_mapper_active",
                                                       MapperTask.file_id == mapper_config_obj.id,
                                                       MapperTask.status == CeleryTaskStatus.received)
            task_id_list = [task.task_id for task in mapper_tasks]
            cancel_task(task_id_list)
            mapper_tasks.update({MapperTask.status: CeleryTaskStatus.revoked})
            db.commit()
        elif mapper_config_obj.set_active_at:
            task = mapper_activate.apply_async(args=(mapper_config_obj.id,),
                                               eta=mapper_config_obj.set_active_at.astimezone(pytz.utc))
            mapper_task = MapperTask(company_id=int(request_dict["company_id"]), task_id=str(task),
                                     file_id=mapper_config_obj.id,
                                     task_name="set_mapper_active",
                                     status=CeleryTaskStatus.received)

            mapper_task_rec = CRUD().add(mapper_task)
            task_id = task.id
        elif request_dict["is_active"]:
            mapper_tasks = db.query(MapperTask).filter(MapperTask.company_id == int(request_dict["company_id"]),
                                                       MapperTask.task_name == "set_mapper_active",
                                                       MapperTask.file_id == mapper_config_obj.id,
                                                       MapperTask.status == CeleryTaskStatus.received)
            task_id_list = [task.task_id for task in mapper_tasks]
            cancel_task(task_id_list)
            mapper_tasks.update({MapperTask.status: CeleryTaskStatus.revoked})
            db.commit()
        response = jsonable_encoder(mapper_config.first())
        mapper_objs = db.query(ProcessMapField).filter(ProcessMapField.file_id == id)
        mapper_objs.delete(synchronize_session=False)
        db.commit()
        mappers = []
        for item in mapper:
            map_rec = ProcessMapField(file_id=id, field_name=item.field_name,
                                      map_field_name=item.map_field_name,
                                      is_ignored=item.is_ignored)
            stored_map_rec = CRUD().add(map_rec)
            mappers.append(jsonable_encoder(stored_map_rec))
        response["mapper"] = mappers
        return response
    except:
        raise FailedToUpdateFileTaskConfig


def create_config(request_body, token, db):
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
        rec = ProcessConfig(**request_dict)
        file_config_rec = CRUD().add(rec)
        if profile_id:
            link_parser_with_profile = MapperProfile(mapper_id=file_config_rec.id, profile_id=profile_id)
            link_parser_with_profile_rec = CRUD().add(link_parser_with_profile)
        if file_config_rec.set_active_at:
            task = mapper_activate.apply_async(args=(file_config_rec.id,),
                                               eta=file_config_rec.set_active_at.astimezone(pytz.utc))
        file_id = file_config_rec.id
        response = jsonable_encoder(file_config_rec)
        mappers = []
        for item in mapper:
            map_rec = ProcessMapField(file_id=file_id, field_name=item.field_name,
                                      map_field_name=item.map_field_name,
                                      is_ignored=item.is_ignored)
            stored_map_rec = CRUD().add(map_rec)
            mappers.append(jsonable_encoder(stored_map_rec))

        response["mapper"] = mappers

        return response
    except Exception as e:
        print(f" \n <====== Exception =====> : \n {str(traceback.format_exc())} \n <==== End Exception ===>  \n")
        print(str(e))
        raise FailedCreateNewFileTaskConfig


def execute_mapper(token, id, db):
    from utils.csv_helpers import CSVHelper

    company_id = token["company"]["id"]
    mapper_config = db.query(ProcessConfig).filter(ProcessConfig.id == id, ProcessConfig.company_id == company_id)

    if not mapper_config.first():
        raise CSVConfigMapperFieldsDoesNotExist

    mapper_config_obj = mapper_config.first()

    csv_helper = CSVHelper(task_id="Ran manual", company_id=company_id, file_id=mapper_config_obj.id,
                           file_name=mapper_config_obj.file_name, file_path=mapper_config_obj.file_path,
                           process_id=mapper_config_obj.process_id)
    x = csv_helper.main()
    if x == "No files":
        return f"{x} NO NEW file with prefix: '{mapper_config_obj.file_name}'  with this path '{mapper_config_obj.file_path}'"

    return f"{x} FILE: '{mapper_config_obj.file_name}' SENT to celery \n \n \n \n " + f"  {str(x)}"


def clone_mapper(token, id, db):
    company_id = token["company"]["id"]
    mapper_config = db.query(ProcessConfig).filter(ProcessConfig.id == id, ProcessConfig.company_id == company_id)
    if not mapper_config.first():
        raise CSVConfigDoesNotExist
    mapper_config_obj = mapper_config.first()
    rec = ProcessConfig(process_id=mapper_config_obj.process_id,
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
    cloned_mapper_id = file_config_rec.id
    mapper_fields = db.query(ProcessMapField).filter(ProcessMapField.file_id == mapper_id).all()

    for field_mapper in mapper_fields:
        field_rec = ProcessMapField(file_id=file_config_rec.id,
                                    field_name=field_mapper.field_name,
                                    map_field_name=field_mapper.map_field_name,
                                    is_ignored=field_mapper.is_ignored
                                    )
        field_mapper_rec = CRUD().add(field_rec)
    mapper_fields = db.query(ProcessMapField).filter(ProcessMapField.file_id == cloned_mapper_id).all()
    cloned_mapper_config = jsonable_encoder(rec)
    cloned_mapper_config["mapper"] = jsonable_encoder(mapper_fields)
    return jsonable_encoder(cloned_mapper_config)


def upload_CSV(request):
    request_dict = request.dict()
    db = CRUD().db_conn()
    rec = FileReceiveHistory(**request_dict)
    CRUD().add(rec)

    data = {
        'image_key': request_dict['image_key'],
        'bucket_name': 'profile-picture'
    }
    return data
