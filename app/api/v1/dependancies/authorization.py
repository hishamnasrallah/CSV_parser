from fastapi import Header, Security
from fastapi.security import APIKeyHeader
from core.exceptions.csv import InvalidAuthentication
from utils.cognito_helper import CognitoJWTHelper
import jwt

# def validate_authorization(authorization: str = Security(APIKeyHeader(name='Authorization'))):
#     jwt_obj = CognitoJWTHelper()
#
#     try:
#         user_info = jwt_obj.verified(authorization)
#     except Exception:
#         raise InvalidAuthentication
#
#     return user_info


def validate_authorization(authorization: str = Security(APIKeyHeader(name='Authorization'))):
    try:
        authorization = authorization.replace("Bearer ", "")
        decoded = jwt.decode(authorization, options={"verify_signature": False})
        # x = jwt.decode(authorization)
        print(decoded)
        return decoded
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        raise InvalidAuthentication
        # raise HTTPException(status_code=400, detail="Invalid token")
