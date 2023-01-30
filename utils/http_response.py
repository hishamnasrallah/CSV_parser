from enum import Enum
from typing import Any
from uuid import uuid4

from fastapi.responses import JSONResponse
from core.constants.response_messages import ResponseConstants


class Language(str, Enum):
    ar: str = "ar"
    en: str = "en"


def http_response(message, status, language: Language = "en", data: Any = None,
                  request_id: str = None, meta: Any = None):
    if not 200 <= status <= 299:
        return http_error_response(error_message=message, status=status, language=language)

    mapper = ResponseConstants.messages_dict()

    if isinstance(message, str):
        try:
            message = mapper[message][language]
        except (KeyError, TypeError):
            pass
    else:
        try:
            message = message[language]
        except (KeyError, TypeError):
            pass

    response = {
        "status": str(status),
        "message": message,
        "data": data if data else [],
        "meta": meta if meta else {},
        "request-id": request_id if request_id else generate_request_id()
    }

    headers = {}
    try:
        headers['x-resource-id'] = str(data.get('id', ''))
    except Exception as e:  # noqa
        headers['x-resource-id'] = ''

    return JSONResponse(status_code=status, content=response, headers=headers)


def http_error_response(error_message, status, language="en", request_id: str = None):
    if 400 <= status <= 499:
        try:
            error_message = error_message[language]
        except (KeyError, TypeError):
            if not isinstance(error_message, str):
                error_message = "undefined message"

    response = {
        "status": str(status),
        "message": error_message,
        "request-id": request_id if request_id else generate_request_id()
    }
    return JSONResponse(status_code=status, content=response)


def generate_request_id():
    return "dev-" + str(uuid4())