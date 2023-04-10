from core.constants.profile import ProfileConstants


class ProfileDoesNotExist(Exception):
    """
    while using try except you should follow the following style
    try:
        try_dody
    except {{specify_exception_class}} as e: # e is a variable will contain the error message of the exception
        exception_body
    """

    def __init__(self, message_key=ProfileConstants.PROFILE_DOES_NOT_EXIST_ERROR):
        self.message_key = message_key
        self.status = 404

        super().__init__(self.message_key, self.status)


class ProfileDoesNotExistBadRequest(Exception):
    def __init__(self, message_key=ProfileConstants.PROFILE_DOES_NOT_EXIST_ERROR):
        self.message_key = message_key
        self.status = 400

        super().__init__(self.message_key, self.status)


class ProfileDeletedError(Exception):
    def __init__(self, message_key=ProfileConstants.PROFILE_ALREADY_DELETED_ERROR):
        self.message_key = message_key
        self.status = 400

        super().__init__(self.message_key, self.status)


class ProfileIsInactive(Exception):
    def __init__(self, message_key=ProfileConstants.PROFILE_IS_INACTIVE_ERROR):
        self.message_key = message_key
        self.status = 400

        super().__init__(self.message_key, self.status)