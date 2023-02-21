import jwt
import datetime

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"

payload = {
    "company_id": "12345",
    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
    "company_name": "hisham co"
}

long_lived_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
print(long_lived_token)

