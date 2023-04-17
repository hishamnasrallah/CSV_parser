from urllib.error import URLError
from requests import request as _request
from requests.exceptions import RequestException, Timeout
from core.exceptions.service import ServiceUnavailable, NotAcceptable
from core.constants.request import Request as RequestConstants
from core.exceptions.csv import InvalidAuthentication
from utils.http_response import http_response


class ImproperlyConfigured(Exception):
    pass


class Broker:
    """
    A class to act as a broker between the gateway and it's services.
    """

    def __init__(self, host, request, name):
        self.request = request
        self.name = name
        self.host = host

    def __str__(self):
        return "%s (%s)" % (self.name, self.host)

    def is_server_error(self, status_code):
        """
        Returns whether the provided HTTP status code is a server error.

        :param status_code: An HTTP status code.
        :type status_code: int

        :return: Whether it is a server error status code.
        :rtype: bool
        """
        return not status_code or 500 <= status_code <= 599

    def is_auth_error(self, status_code):
        """
        Returns whether the provided HTTP status code is an auth error.

        :param status_code: An HTTP status code.
        :type status_code: int

        :return: Whether it is an auth error.
        :rtype: bool
        """
        return status_code in (401, 403)

    def get_headers(self, extras):
        """
        Returns a dictionary of HTTP Headers to send with the new :class: `Request`.

        :param extras:
        :type extras: dict

        :return: A dictionary of HTTP Headers.
        :rtype: dict
        """
        defaults = {
            "Authorization": self.request.headers.get("Authorization", None)
        }

        return {**defaults, **extras}

    def get_params(self, extras):
        """
        Returns a dictionary of query params to send with the new :class: `Request`.

        :param extras:
        :type extras: dict

        :return: A dictionary of query params.
        :rtype: dict
        """
        defaults = {key: value for key, value in self.request.query_params}

        return {**defaults, **extras}

    def get_data(self, data):
        """
        Returns a JSON data to send in the body of the new :class:`Request` object.

        :param data:
        :type data: dict

        :return: A JSON data.
        :rtype: dict
        """
        return {**data}

    def parse_url(self, *sections):
        """
        Returns an absolute URL string for the new `Request` object.

        :return: An absolute URL string.
        :rtype: str
        """
        sections = (self.host,) + sections

        return "/".join(map(str, sections))

    def send(self, method, url, response_message_key, headers=None, params=None, data=None,
             timeout=RequestConstants.REQUEST_TIMEOUT,
             accept=RequestConstants.CONTENT_TYPE):
        """
        Constructs and sends a :class:`Request<requests.models.Request>` object.

        :param method: Method for the new :class:`Request` object.
        :type method: str

        :param url: URL for the new :class:`Request` object.
        :type url: str

        :param headers: (optional) Dictionary of HTTP Headers to send
            with the :class:`Request` object.
        :type headers: dict|None

        :param params: (optional) Dictionary to be sent in the query
            string for the :class:`Request` object.
        :type params: dict|None

        :param data: (optional) JSON data to send in the body of the :class:`Request` object.
        :type data: dict|None

        :param timeout: (optional) How many seconds to wait for the server to send data
            before giving up, as a float, or a :ref:`(connect timeout, read timeout)`
            tuple. The default value is 10.0 seconds
        :type timeout: (float, float)|float

        :param accept: (optional) The expected content type, default is "application/json".
        :type accept: str

        :return: HttpResponse object.
        :rtype: HttpResponse
        """
        headers = {} if headers is None else headers
        params = {} if params is None else params
        data = {} if data is None else data

        kwargs = {
            "headers": self.get_headers(headers),
            "params": self.get_params(params),
            "json": self.get_data(data),
            "timeout": timeout
        }

        try:
            response = _request(method, url, **kwargs)
        except (Timeout, RequestException, URLError) as e:
            raise ServiceUnavailable

        status_code = response.status_code
        content_type = response.headers.get("content-type", None)

        if self.is_server_error(status_code):
            raise ServiceUnavailable

        if not content_type == accept:
            raise NotAcceptable

        if self.is_auth_error(status_code):
            raise InvalidAuthentication

        return http_response(data=response.content, message_key=response_message_key,
                             status=status_code)

    def make_url(self, *args):
        url = "%s" % self.host

        for arg in args:
            url += "/%s" % arg

        return url
