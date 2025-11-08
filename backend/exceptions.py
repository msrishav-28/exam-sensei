"""
Custom exceptions for ExamSensei
Provides specific error types for better error handling
"""
from fastapi import HTTPException, status


class ExamSenseiException(Exception):
    """Base exception for ExamSensei"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(ExamSenseiException):
    """Authentication failed"""
    pass


class AuthorizationError(ExamSenseiException):
    """User not authorized for this action"""
    pass


class ResourceNotFoundError(ExamSenseiException):
    """Requested resource not found"""
    pass


class ValidationError(ExamSenseiException):
    """Data validation failed"""
    pass


class ExternalServiceError(ExamSenseiException):
    """External service (Ollama, scraper) failed"""
    pass


class DatabaseError(ExamSenseiException):
    """Database operation failed"""
    pass


class RateLimitError(ExamSenseiException):
    """Rate limit exceeded"""
    pass


# HTTP Exception helpers
def http_exception(status_code: int, message: str, details: dict = None):
    """Create HTTP exception with details"""
    return HTTPException(
        status_code=status_code,
        detail={
            "message": message,
            "details": details or {}
        }
    )


def not_found(resource: str, identifier: str = None):
    """404 Not Found"""
    message = f"{resource} not found"
    if identifier:
        message += f": {identifier}"
    return http_exception(status.HTTP_404_NOT_FOUND, message)


def unauthorized(message: str = "Authentication required"):
    """401 Unauthorized"""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"}
    )


def forbidden(message: str = "Access forbidden"):
    """403 Forbidden"""
    return http_exception(status.HTTP_403_FORBIDDEN, message)


def bad_request(message: str, details: dict = None):
    """400 Bad Request"""
    return http_exception(status.HTTP_400_BAD_REQUEST, message, details)


def internal_error(message: str = "Internal server error"):
    """500 Internal Server Error"""
    return http_exception(status.HTTP_500_INTERNAL_SERVER_ERROR, message)


def service_unavailable(service: str):
    """503 Service Unavailable"""
    return http_exception(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        f"{service} is currently unavailable"
    )


def rate_limit_exceeded():
    """429 Too Many Requests"""
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Rate limit exceeded. Please try again later.",
        headers={"Retry-After": "60"}
    )
