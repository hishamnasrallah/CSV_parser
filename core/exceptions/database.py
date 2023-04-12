class DataBaseConnectionException(Exception):
    def __init__(self, message="invalid database connections"):
        self.message = message
        super().__init__(self.message)
