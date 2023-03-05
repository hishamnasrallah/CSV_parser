import boto3 as boto3
import base64
from botocore.exceptions import ClientError
import ast
import os


class AWSConfig:
    AWS_REGION_NAME = os.environ.get('AWS_REGION_NAME', 'eu-central-1')


class AWSSecretManger(object):
    def __init__(self):
        self._session = boto3.session.Session()
        self.client = self._session.client(
            service_name='secretsmanager',
            region_name=AWSConfig.AWS_REGION_NAME
        )
    # Use this code snippet in your app.
    # If you need more information about configurations or implementing the sample code, visit the AWS docs:
    # https://aws.amazon.com/developers/getting-started/python/

    def get_secret(self, secret_name):
        # region_name = "eu-central-1"

        # Create a Secrets Manager client
        # session = boto3.session.Session()
        # client = session.client(
        #     service_name='secretsmanager',
        #     region_name=region_name
        # )

        # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
        # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        # We rethrow the exception by default.
        # get_secret_value_response = self.client.get_secret_value(
        #     SecretId=secret_name
        # )
        # print(get_secret_value_response)
        try:
            # test = self.client
            get_secret_value_response = self.client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            return {}
            # if e.response['Error']['Code'] == 'DecryptionFailureException':
            #     # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            #     # Deal with the exception here, and/or rethrow at your discretion.
            #     raise e
            # elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            #     # An error occurred on the server side.
            #     # Deal with the exception here, and/or rethrow at your discretion.
            #     raise e
            # elif e.response['Error']['Code'] == 'InvalidParameterException':
            #     # You provided an invalid value for a parameter.
            #     # Deal with the exception here, and/or rethrow at your discretion.
            #     raise e
            # elif e.response['Error']['Code'] == 'InvalidRequestException':
            #     # You provided a parameter value that is not valid for the current state of the resource.
            #     # Deal with the exception here, and/or rethrow at your discretion.
            #     raise e
            # elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            #     # We can't find the resource that you asked for.
            #     # Deal with the exception here, and/or rethrow at your discretion.
            #     raise e
        # else:
            # Decrypts secret using the associated KMS key.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            secrets = ast.literal_eval(secret)
            return secrets
        else:
            return {}
            # decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])

        # Your code goes here.
