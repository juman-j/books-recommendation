class MissingEnvironmentVariablesError(Exception):
    def __init__(self, message="Necessary environmental variables are missing."):
        self.message = message
        super().__init__(self.message)


class UnknownClient(Exception):
    def __init__(self, message="The client belongs to an unknown class."):
        self.message = message
        super().__init__(self.message)


class InvalidClientConfiguration(Exception):

    def __init__(self, message="You must select exactly one of open_ai or azure."):
        self.message = message
        super().__init__(self.message)


class DBError(Exception):
    def __init__(self, message="Database interaction error."):
        self.message = message
        super().__init__(self.message)


class ValueNotFoundError(Exception):
    def __init__(self, message="Value not found in the database."):
        self.message = message
        super().__init__(self.message)


class ESDBConnectionError(Exception):
    def __init__(self, message="ESDB connection error."):
        self.message = message
        super().__init__(self.message)


class InsertionError(Exception):
    def __init__(self, message="Failed to send data to the database."):
        self.message = message
        super().__init__(self.message)
