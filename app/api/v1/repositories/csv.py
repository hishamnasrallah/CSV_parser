# from asyncpg import RaiseError
import traceback

from fastapi import HTTPException, status
# from fastapi.encoders import jsonable_encoder
# from sqlalchemy import and_
from fastapi.encoders import jsonable_encoder
# import json
from app.api.v1.models import FileReceiveHistory, ProcessConfig, ProcessMapField
from app.api.v1.repositories.common import CRUD
from app.api.v1.serializers.csv import FileTaskConfigRequest, FileTaskConfig
from core.exceptions.csv import CSVConfigDoesNotExist, FailedCreateNewFileTaskConfig


def get_dashboard(token, db):
    configs = db.query(ProcessConfig).filter(ProcessConfig.company_id == token["company_id"]).all()
    jsonable_encoder(configs)
    return jsonable_encoder(configs)


def delete_config(id, token, db):
    config = db.query(ProcessConfig).filter(ProcessConfig.id == id, ProcessConfig.company_id == token["company_id"])
    if not config.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=CSVConfigDoesNotExist().message_key)
    else:
        config.delete(synchronize_session=False)
        db.commit()
        return 'deleted'


def get_file_mapper(file_id, db=CRUD().db_conn()):
    mapper = db.query(ProcessMapField).filter(ProcessMapField.file_id == file_id).all()
    print(mapper)
    return mapper


def get_file_history(file_id, file_name=None, db=CRUD().db_conn()):
    history = db.query(FileReceiveHistory).filter(FileReceiveHistory.file_id == file_id,
                                                  FileReceiveHistory.file_name_as_received == file_name)
    return history


def get_file_process_history(file_id, db):
    history = db.query(FileReceiveHistory).filter(FileReceiveHistory.file_id == file_id).all()
    jsonable_encoder(history)
    return jsonable_encoder(history)


def create_config(request_body, token, db):
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
