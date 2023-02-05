# from asyncpg import RaiseError
import traceback

from fastapi import HTTPException, status
# from fastapi.encoders import jsonable_encoder
# from sqlalchemy import and_
from fastapi.encoders import jsonable_encoder
# import json
from app.api.models import FileReceiveHistory, ProcessConfig, ProcessMapField
from app.api.repositories.common import CRUD
from app.brokers.decapolis_core import CoreApplicationBroker
from core.exceptions.csv import CSVConfigDoesNotExist, FailedCreateNewFileTaskConfig


def mappers_configs(token, db):
    """

    :param token: you have to pass token to this function to extract company_id from it
    :param db: is the database connection
    :return: it will return all mapping configurations for the specific company
    """

    configs = db.query(ProcessConfig).filter(ProcessConfig.company_id == token["company_id"]).all()
    jsonable_encoder(configs)
    return jsonable_encoder(configs)


def mapper_details(token, id, db):
    """

    :param token: you have to pass token to this function to extract company_id from it.
    :param id: it should be the mapper configuration id
    :param db: is the database connection
    :return: the specfic mapper configuration details with field mapping
    """
    mapper_config = db.query(ProcessConfig).filter(ProcessConfig.company_id == token["company_id"], ProcessConfig.id==id).first()
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
    config = db.query(ProcessConfig).filter(ProcessConfig.id == id, ProcessConfig.company_id == token["company_id"])
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
    print(mapper)
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


# def get_file_process_history(file_id, db):
#     """
#
#     :param file_id: mapper configuration id
#     :param db: the database connection
#     :return: all records history for specific file configuration
#     """
#     history = db.query(FileReceiveHistory).filter(FileReceiveHistory.file_id == file_id).all()
#     jsonable_encoder(history)
#     return jsonable_encoder(history)


def get_company_processes(token, request):
    """

    :param token: to extract company_id from it.
    :param request: request as received to use it in the broker
    :return: the response from the broker that call an api from the core application
    """
    company_id = token["company_id"]
    broker = CoreApplicationBroker(request)
    response = broker.get_company_processes(company_id=company_id, response_message_key=200)
    jsonable_encoder(response)
    return jsonable_encoder(response)


def create_config(request_body, token, db):
    """

    :param request_body: the data that sent to the api as json
    :param token: to extract company_id from it
    :return: new configuration
    """
    request_dict = request_body.dict()
    request_dict["company_id"] = token["company_id"]
    try:
        mapper = request_dict.pop("mapper", None)
        print(request_dict)
        rec = ProcessConfig(**request_dict)
        file_config_rec = CRUD().add(rec)
        file_id = file_config_rec.id
        for key, value in mapper.items():
            map_rec = ProcessMapField(file_id=file_id, field_name=key, map_field_name=value)
            CRUD().add(map_rec)
        # mapper_rec =
    except Exception as e:
        print(f" \n <====== Exception =====> : \n {str(traceback.format_exc())} \n <==== End Exception ===>  \n")
        print(str(e))
        raise FailedCreateNewFileTaskConfig


def upload_CSV(request):

    print(request)
    request_dict = request.dict()

    db = CRUD().db_conn()
    # img = db.query(CSVUploadModel).filter(CSVUploadModel.cognito_sub == sub)
    # image = img.first()

    # if image:
    #     raise CognitoSubExist()
    rec = FileReceiveHistory(**request_dict)
    CRUD().add(rec)

    data = {
        'image_key': request_dict['image_key'],
        'bucket_name': 'profile-picture'
    }
    return data
