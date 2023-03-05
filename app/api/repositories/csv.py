import traceback
from datetime import datetime

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from app.api.models import FileReceiveHistory, ProcessConfig, ProcessMapField
from app.api.repositories.common import CRUD
from app.api.v1.serializers.csv import MapperDetail
from app.brokers.decapolis_core import CoreApplicationBroker
from core.exceptions.csv import CSVConfigDoesNotExist, FailedCreateNewFileTaskConfig


def mappers_configs(token, db):
    """

    :param token: you have to pass token to this function to extract company_id from it
    :param db: is the database connection
    :return: it will return all mapping configurations for the specific company
    """

    configs = db.query(ProcessConfig).filter(ProcessConfig.company_id == token["company"]["id"]).all()
    jsonable_encoder(configs)
    return jsonable_encoder(configs)


def mapper_details(token, id, db):
    """

    :param token: you have to pass token to this function to extract company_id from it.
    :param id: it should be the mapper configuration id
    :param db: is the database connection
    :return: the specfic mapper configuration details with field mapping
    """
    mapper_config = db.query(ProcessConfig).filter(ProcessConfig.company_id == token["company"]["id"], ProcessConfig.id==id).first()
    mapper_fields = db.query(ProcessMapField).filter(ProcessMapField.file_id == id).all()
    mapper_config = jsonable_encoder(mapper_config)
    mapper_config["mapper_fields"] = jsonable_encoder(mapper_fields)
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


def create_file_history(file_id, file_size, file_name_as_received, task_id="1"):
    history_rec = FileReceiveHistory(file_id=file_id, file_size_kb=file_size, file_name_as_received=file_name_as_received, task_id=task_id)
    history_rec = CRUD().add(history_rec)
    return history_rec


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



def create_config(request_body, token, db):
    """

    :param request_body: the data that sent to the api as json
    :param token: to extract company_id from it
    :return: new configuration
    """
    request_dict = request_body.dict()
    request_dict["company_id"] = token["company"]["id"]
    try:
        mapper = request_dict.pop("mapper", None)
        rec = ProcessConfig(**request_dict)
        file_config_rec = CRUD().add(rec)
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
