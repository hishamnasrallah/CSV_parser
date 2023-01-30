from core.constants.service import Service


class ServiceUnavailable(Exception):
    """
    while using try except you should follow the following style
    try:
        try_dody
    except {{specify_exception_class}} as e: # e is a variable will contain the error message of the exception
        exception_body
    """

    def __init__(self, message=Service.NOT_AVAILABLE):
        self.message = message
        self.status = 400
        super().__init__(self.message, self.status)


class NotAcceptable(Exception):
    """
    while using try except you should follow the following style
    try:
        try_dody
    except {{specify_exception_class}} as e: # e is a variable will contain the error message of the exception
        exception_body
    """

    def __init__(self, message=Service.NOT_ACCESSIBLE):
        self.message = message
        self.status = 400
        super().__init__(self.message, self.status)
