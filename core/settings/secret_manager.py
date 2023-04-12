import ast
import os

import boto3

from botocore.exceptions import ClientError


class AWSConfig:
    AWS_REGION_NAME = os.environ.get('AWS_REGION_NAME', 'eu-central-1')


class AWSSecretManger(object):
    def __init__(self):
        self._session = boto3.session.Session()
        self.client = self._session.client(
            service_name='secretsmanager',
            region_name=AWSConfig.AWS_REGION_NAME
        )

    def get_secret(self, secret_name):
        try:
            get_secret_value_response = self.client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            return {}
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            secrets = ast.literal_eval(secret)
            return secrets
        else:
            return {}
