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
