from app.brokers.base import Broker


class ConfigurationsBroker(Broker):
    """
    A broker to handle communication with the `Activities` service.
    """
    HOST = "127.0.0.1:8001/api"

    def __init__(self, request):
        name = "Configurations"
        super(ConfigurationsBroker, self).__init__(self.HOST, request, name)

    # GET: /countries
    def get_countries(self, response_message_key, **kwargs):
        url = self.parse_url("countries")

        return self.send("GET", url, response_message_key, **kwargs, timeout=10)

    # GET: /countries/{alpha_2}
    def get_country(self, alpha_2, response_message_key, **kwargs):
        url = self.parse_url("countries", alpha_2)

        return self.send("GET", url, response_message_key, **kwargs, timeout=10)
