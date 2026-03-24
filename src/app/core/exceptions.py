class BusinessException(Exception):
    """Base exception for all business rule violations"""
    status_code: int = 400
    detail: str = "Business rule error"

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)



# Account Service Exceptions
class InvalidCredentialsError(BusinessException):
    detail = "Invalid Credentials"
    status_code = 401


class EmailAlreadyExistsError(BusinessException):
    detail = "Email already exists"
    status_code = 409


class AccessDeniedError(BusinessException):
    detail = "Access denied"
    status_code = 403


class InvalidAccessTokenError(BusinessException):
    detail = "Invalid or expired access token."
    status_code = 400


class RequireAdminError(BusinessException):
    detail = "Only admins can access this feature"
    status_code = 401
