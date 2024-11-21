class BaseCustomError(Exception):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self):
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class UnsupportedFileError(BaseCustomError):
    def __init__(
        self, message: str = "Unsupported file format", details: dict | None = None
    ):
        super().__init__(message=message, details=details)
