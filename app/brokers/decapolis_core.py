from app.brokers.base import Broker
import requests
import os

from utils.sftp_token import SFTP_TOKEN


class CoreApplicationBroker(Broker):
    """
    A broker to handle communication with the `decapolis core` application.
    """
    HOST = os.environ.get('PRIVATE_CORE_ENDPOINT')

    def __init__(self, request=None):
        name = "Core Application"
        super(CoreApplicationBroker, self).__init__(self.HOST, request, name)

    # // TODO: the following brokeres need to be developed in core application
    # GET: /{company_id}/processes
    def get_company_processes(self, company_id, response_message_key, **kwargs):
        url = self.parse_url(company_id, "processes")
        return self.send("GET", url, response_message_key, **kwargs, timeout=10)

    # GET: /{company_id}/processes/{process_id}
    def get_company_process_fields(self, company_id, process_id, response_message_key, **kwargs):
        url = self.parse_url({company_id}, "processes", {process_id})
        return self.send("GET", url, response_message_key, **kwargs, timeout=10)


def send_collected_data(company_id, process_id, data):
    host = os.environ.get('PRIVATE_CORE_ENDPOINT')
    # headers = {
    #     "Host": "parser-dev.decapolis.io"
    # }
    url = f"https://dev.app.decapolis.io/api/v2/process/{process_id}/company/{company_id}/active_process/submit"
    response = requests.request("POST", url, data=data)
    return response
