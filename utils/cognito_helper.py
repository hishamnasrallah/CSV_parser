import cognitojwt

from core.settings.base import settings


class CognitoJWTHelper:

    def __init__(self):
        self.userpool_id = settings.aws_cognito_settings["AWS_USERPOOL_ID"]
        self.region = settings.aws_cognito_settings["AWS_REGION_NAME"]
        self.app_client_id = settings.aws_cognito_settings["AWS_APP_CLIENT_ID"]
        self.id_token = None

    def verified(self, id_token):
        self.id_token = id_token

        verified_claims: dict = cognitojwt.decode(
            self.id_token,
            self.region,
            self.userpool_id,
            app_client_id=self.app_client_id,  # Optional
            testmode=True  # Disable token expiration check for testing purposes
        )
        return verified_claims
