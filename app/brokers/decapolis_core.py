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
    import requests
    import json

    url = "http://dev-app-private.decapolis.io/api/v2/process/2487/comapny/121/active_process/submit"

    payload = json.dumps({
        "crop_code": "qwe",
        "variety": "qwe",
        "production_date": "qwe",
        "expired_date": "qwe",
        "treatment": "qwe",
        "origin_certification": "qwe",
        "crop_name": "qwe",
        "scouting_date": "qwe",
        "nursery_number": "qwe",
        "bench_number": "qwe",
        "pest_and_disease": "qwe",
        "severity_scoring": "qwe",
        "instructions_given_to_spray_team": "qwe",
        "acknowledged_by_operations_manager": "qwe",
        "delivery_date": "qwe",
        "variety_code": "qwe",
        "block_id": "qwe",
        "number_of_trays": "qwe",
        "sowing_date": "qwe",
        "sowing_quantity": "qwe",
        "start_time": "qwe",
        "end_time": "qwe",
        "qa_production_manager_order": "qwe",
        "date_of_qa_production_manager_order": "qwe",
        "received_by_technical_farm_manager": "qwe",
        "date_of_receiving_by_technical_farm_manager": "qwe",
        "compost_quantity": "qwe",
        "technical_farm_manager_name": "qwe",
        "signature_date_of_technical_farm_manager": "qwe",
        "operations_manager_name": "qwe",
        "signature_dare_of_operations_manager": "qwe",
        "seed_germination_done": "qwe",
        "espaneol_record_irrigations_date": "qwe",
        "temp_min": "qwe",
        "tempmax": "qwe",
        "temp_awg_24h": "qwe",
        "temp_awg_day": "qwe",
        "temp_awg_night": "qwe",
        "relhumid_min": "qwe",
        "relhumid_max": "qwe",
        "humid_def_min_gkg": "qwe",
        "humid_def_max_gkg": "qwe",
        "report_no": "qwe",
        "time": "qwe",
        "gh": "qwe",
        "plot": "qwe",
        "trade_name": "qwe",
        "active_ingredient": "qwe",
        "actual_rate_of_use_1000_m2": 123,
        "reason_for_application": "qwe",
        "p_or_c": "qwe",
        "weather_condition": "qwe",
        "safe_harvest_date": "qwe",
        "operators_names_and_tanak_number": "qwe",
        "signed_by": "qwe",
        "planet_moved_to_table_kept_inside_nursery_for_30_40_days_prior_to_transplantation": "qwe",
        "of_germination_below_standard": "qwe",
        "crop": "qwe",
        "remarks": "qwe"
    })
    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc4MDk5MDk4LCJqdGkiOiI5OGYyYmEzMGZiMDI0OGM5Yjg5NjA5MDBiNDQ3ZWRiOCIsInVzZXJfaWQiOjY0NSwidXNlcl9mdWxsX25hbWUiOiIifQ.EW3ZzGWaUJQeBCc4NnUVEIoxzOQz1irt791Lz4stXOk',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    # host = os.environ.get('PRIVATE_CORE_ENDPOINT')
    # headers = {
    #     "Host": "parser"
    # }
    # url = f"http://dev-app-private.decapolis.io/api/v2/process/{process_id}/company/{company_id}/active_process/submit"
    # response = requests.request("POST", url, headers=headers, data=data)
    return response.text
