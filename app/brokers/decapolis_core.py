from app.brokers.base import Broker
import os


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
