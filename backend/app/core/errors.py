"""Application errors with safe, user-facing guidance."""


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        action: str,
        status_code: int = 400,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action
        self.status_code = status_code
        self.retryable = retryable
