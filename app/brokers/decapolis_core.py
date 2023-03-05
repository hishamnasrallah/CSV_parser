from app.brokers.base import Broker
import requests


class CoreApplicationBroker(Broker):
    """
    A broker to handle communication with the `decapolis core` application.
    """
    HOST = "https://dev.app.decapolis.io/api/v2"

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

    # POST: /process/process_id/active_process/submit
    def post_collected_data(self, process_id, response_message_key, data, **kwargs):
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgwNTE5MTI1LCJqdGkiOiJiNTFiZWFhZTgzZTA0YTY5OTcyYzEzMGQ3NWU4MDcxNCIsInVzZXJfaWQiOjEyOCwidXNlcl9mdWxsX25hbWUiOiIiLCJjb21wYW55Ijp7ImlkIjoxMjEsIm5hbWUiOiJEZWxtb250ZSIsImxvZ28iOm51bGwsInVzZXIiOnsiaXNfc3RhZmYiOmZhbHNlfSwidXNlX3ByZV9wcmludGVkX2xhYmVscyI6dHJ1ZSwidXNlX21hbnVhbF9xcmNvZGVfcHJpbnRpbmciOnRydWV9fQ.lCk5RQpzftquMGpLJ2ra_nGXEhu2Mg88iNugctXpEts",
        }

        url = self.parse_url("process", process_id, "active_process", "submit")
        return self.send("POST", url, response_message_key, headers=headers, data=data, timeout=10)


def send_collected_data(company_id, process_id, data):
    url = "http://backend-app:8000//api/v2/process/1/active_process/submit"
    payload = {"process_id": process_id, "data": data}
    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgwNTE5MTI1LCJqdGkiOiJiNTFiZWFhZTgzZTA0YTY5OTcyYzEzMGQ3NWU4MDcxNCIsInVzZXJfaWQiOjEyOCwidXNlcl9mdWxsX25hbWUiOiIiLCJjb21wYW55Ijp7ImlkIjoxMjEsIm5hbWUiOiJEZWxtb250ZSIsImxvZ28iOm51bGwsInVzZXIiOnsiaXNfc3RhZmYiOmZhbHNlfSwidXNlX3ByZV9wcmludGVkX2xhYmVscyI6dHJ1ZSwidXNlX21hbnVhbF9xcmNvZGVfcHJpbnRpbmciOnRydWV9fQ.lCk5RQpzftquMGpLJ2ra_nGXEhu2Mg88iNugctXpEts'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response
