"""
HTTP error helpers — all return HTTPException with a consistent envelope:

    {"detail": {"message": "...", "details": {...}}}

so callers (frontend) only ever have to parse one shape.
"""
from typing import Optional

from fastapi import HTTPException, status


class ExamSenseiException(Exception):
    """Base exception for ExamSensei domain errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(ExamSenseiException):
    pass


class AuthorizationError(ExamSenseiException):
    pass


class ResourceNotFoundError(ExamSenseiException):
    pass


class ValidationError(ExamSenseiException):
    pass


class ExternalServiceError(ExamSenseiException):
    pass


class DatabaseError(ExamSenseiException):
    pass


class RateLimitError(ExamSenseiException):
    pass


def _envelope(message: str, details: Optional[dict] = None) -> dict:
    return {"message": message, "details": details or {}}


def http_exception(
    status_code: int,
    message: str,
    details: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=_envelope(message, details),
        headers=headers,
    )


def not_found(resource: str, identifier: Optional[str] = None) -> HTTPException:
    msg = f"{resource} not found" + (f": {identifier}" if identifier else "")
    return http_exception(status.HTTP_404_NOT_FOUND, msg)


def unauthorized(message: str = "Authentication required") -> HTTPException:
    return http_exception(
        status.HTTP_401_UNAUTHORIZED,
        message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden(message: str = "Access forbidden") -> HTTPException:
    return http_exception(status.HTTP_403_FORBIDDEN, message)


def bad_request(message: str, details: Optional[dict] = None) -> HTTPException:
    return http_exception(status.HTTP_400_BAD_REQUEST, message, details)


def internal_error(message: str = "Internal server error") -> HTTPException:
    return http_exception(status.HTTP_500_INTERNAL_SERVER_ERROR, message)


def service_unavailable(service: str) -> HTTPException:
    return http_exception(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        f"{service} is currently unavailable",
    )


def rate_limit_exceeded() -> HTTPException:
    return http_exception(
        status.HTTP_429_TOO_MANY_REQUESTS,
        "Rate limit exceeded. Please try again later.",
        headers={"Retry-After": "60"},
    )
