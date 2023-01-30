from core.constants.csv import CSVConstants


class CSVConfigDoesNotExist(Exception):
    """
    while using try except you should follow the following style
    try:
        try_dody
    except {{specify_exception_class}} as e: # e is a variable will contain the error message of the exception
        exception_body
    """

    def __init__(self, message_key=CSVConstants.CONFIG_DOES_NOT_EXIST_ERROR):
        self.message_key = message_key
        self.status = 404

        super().__init__(self.message_key, self.status)


class FailedCreateNewFileTaskConfig(Exception):
    def __init__(self, message_key=CSVConstants.FAILED_CREATE_FILE_TASK_CONFIG):
        self.message_key = message_key
        self.status = 401

        super().__init__(self.message_key, self.status)

class InvalidAuthentication(Exception):
    def __init__(self, message_key=CSVConstants.INVALID_AUTHENTICATION):
        self.message_key = message_key
        self.status = 401

        super().__init__(self.message_key, self.status)
#
#
# class InvalidPhoneNumber(Exception):
#     def __init__(self, message_key=UserConstants.INVALID_PHONE_NUMBER):
#         self.message_key = message_key
#         self.status = 401
#
#         super().__init__(self.message_key, self.status)

