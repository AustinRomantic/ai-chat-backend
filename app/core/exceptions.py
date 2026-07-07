class BizException(Exception):
    def __init__(self, message: str, code: int = 400, error_code: str = "BIZ_ERROR"):
        self.message = message
        self.code = code
        self.error_code = error_code
        super().__init__(message)