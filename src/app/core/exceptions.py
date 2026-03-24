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

class UserNotFoundError(BusinessException):
    detail = "User not found"
    status_code = 404


class AccessDeniedError(BusinessException):
    detail = "Access denied"
    status_code = 403


class InvalidAccessTokenError(BusinessException):
    detail = "Invalid or expired access token."
    status_code = 400


class RequireAdminError(BusinessException):
    detail = "Only admins can access this feature"
    status_code = 401


# Order Service Exceptions

class OrderCancellationTimeExceededError(BusinessException):
    detail = "The time allowed to cancel the order has already passed."
    status_code = 401


class OrderDoesNotBelongToUserError(BusinessException):
    detail = "The current user is not the order holder who wishes to cancel the order."
    status_code = 409


class PermissionDeniedError(BusinessException):
    detail = "You do not have permission to perform this action."
    status_code = 403


class OrderItemDoesNotBelongToOrderError(BusinessException):
    detail = "The order item does not belong to the specified order."
    status_code = 400


class OrderNotFoundError(BusinessException):
    detail = "The specified order was not found."
    status_code = 404


class OrderItemNotFoundError(BusinessException):
    detail = "The specified order item was not found."
    status_code = 404


class OrderEqualToZeroError(BusinessException):
    detail = "Order value equal to or less than zero"
    status_code = 400


# Payment Service Exceptions

class PaymentNotFoundError(BusinessException):
    detail = "Payment not found"
    status_code = 404


class InvalidPayloadError(BusinessException):
    detail = "Invalid payload"
    status_code = 400


class InvalidSignatureError(BusinessException):
    detail = "Invalid signature"
    status_code = 400