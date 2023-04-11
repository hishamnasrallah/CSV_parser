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


class CSVConfigMapperFieldsDoesNotExist(Exception):
    """
    while using try except you should follow the following style
    try:
        try_dody
    except {{specify_exception_class}} as e: # e is a variable will contain the error message of the exception
        exception_body
    """

    def __init__(self, message_key=CSVConstants.CONFIG_MAPPER_FIELDS_DOES_NOT_EXIST_ERROR):
        self.message_key = message_key
        self.status = 404

        super().__init__(self.message_key, self.status)


class FailedCreateNewFileTaskConfig(Exception):
    def __init__(self, message_key=CSVConstants.FAILED_CREATE_FILE_TASK_CONFIG):
        self.message_key = message_key
        self.status = 401

        super().__init__(self.message_key, self.status)

class FailedToUpdateFileTaskConfig(Exception):
    def __init__(self, message_key=CSVConstants.FAILED_UPDATE_FILE_TASK_CONFIG):
        self.message_key = message_key
        self.status = 401

        super().__init__(self.message_key, self.status)

class InvalidAuthentication(Exception):
    def __init__(self, message_key=CSVConstants.INVALID_AUTHENTICATION):
        self.message_key = message_key
        self.status = 401

        super().__init__(self.message_key, self.status)


class CantChangeStatusNoProfileAssigned(Exception):
    def __init__(self, message_key=CSVConstants.CANT_CHANGE_STATUS_NO_ASSIGNED_PROFILE):
        self.message_key = message_key
        self.status = 400

        super().__init__(self.message_key, self.status)


class NoProfileAssigned(Exception):
    def __init__(self, message_key=CSVConstants.NO_ASSIGNED_PROFILE):
        self.message_key = message_key
        self.status = 400

        super().__init__(self.message_key, self.status)


class ProfileAlreadyDeleted(Exception):
    def __init__(self, message_key=CSVConstants.PROFILE_ALREADY_DELETED_ERROR):
        self.message_key = message_key
        self.status = 400

        super().__init__(self.message_key, self.status)

class CantChangeStatusProfileIsInactive(Exception):
    def __init__(self, message_key=CSVConstants.PROFILE_IS_INACTIVE_ERROR):
        self.message_key = message_key
        self.status = 400

        super().__init__(self.message_key, self.status)


class SetActiveDateMustBeInFuture(Exception):
    def __init__(self, message_key=CSVConstants.SET_ACTIVE_DATE_SOULD_BE_IN_FUTURE, field_name=None):
        if field_name:
            self.message_key = {field_name: message_key}
        else:
            self.message_key = message_key
        self.status = 400
        super().__init__(self.message_key, self.status, field_name)



class HistoryDoesNotExist(Exception):

    def __init__(self, message_key=CSVConstants.HISTORY_DOESNT_EXISTS):
        self.message_key = message_key
        self.status = 404

        super().__init__(self.message_key, self.status)