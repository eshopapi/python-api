"""Exceptions"""

from typing import Dict, Optional
from fastapi import HTTPException, status
from starlette.status import HTTP_401_UNAUTHORIZED

from shopapi.config import Config


class ExtendedHTTPException(HTTPException):
    """Display error code together with detail"""

    def __init__(
        self,
        status_code: Optional[int] = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[str] = None,
        headers: Optional[Dict] = None,
    ):
        status_code = status_code or status.HTTP_500_INTERNAL_SERVER_ERROR
        detail = detail or "Unexpected error ocurred"
        headers = headers or {}
        super().__init__(
            status_code=status_code, headers=headers, detail={"message": detail, "code": self.__class__.__name__}
        )


class UnexpectedException(ExtendedHTTPException):
    """Raised whenever an unexpected error ocurrs. Displays support contact to the user."""

    def __init__(
        self, status_code: Optional[int] = status.HTTP_500_INTERNAL_SERVER_ERROR, detail: Optional[str] = None
    ):
        status_code = status_code or status.HTTP_500_INTERNAL_SERVER_ERROR
        detail = detail or f"Unexpected error ocurred. Please contact us at {Config.support_contact}."
        super().__init__(status_code=status_code, detail=detail)


class LoginError(ExtendedHTTPException):
    """Raised whenever login-specific error ocurrs"""

    def __init__(self, status_code: Optional[int] = status.HTTP_401_UNAUTHORIZED, detail: Optional[str] = None):
        status_code = status_code or status.HTTP_401_UNAUTHORIZED
        detail = detail or "Unexpected error ocurred when processing your login request"
        super().__init__(status_code=status_code, detail=detail)


class LoginReusedEmailError(LoginError):
    """Raised if the user is attempting to login using a different provider with the same e-email"""

    def __init__(self, email: Optional[str] = None):
        detail = (
            f"You already are registered using specified e-mail address ({email}), "
            "but you used a different means of login previously "
            "(did you try both password and 3rd party providers' login?)."
        )
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UserAlreadyExists(ExtendedHTTPException):
    """Raised when user is about to register but his email already exists"""

    def __init__(self, email: Optional[str] = None):
        detail = f"User with specified e-mail ({email}) already exists"
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class CredentialsException(ExtendedHTTPException):
    """Raised when credentials provided by the user cannot be verified"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthenticationException(ExtendedHTTPException):
    """Raised when the user could not be authenticated"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


class SecurityException(ExtendedHTTPException):
    """Raised when a suspection that someone is trying to do something ugly rises"""

    def __init__(self, status_code: Optional[int] = status.HTTP_401_UNAUTHORIZED, detail: Optional[str] = None):
        status_code = status_code or status.HTTP_401_UNAUTHORIZED
        detail = detail or (
            "Security error was raised, this may happen when something unexpected ocurrs, "
            "that looks like someone is trying to access something they are not allowed to"
        )
        super().__init__(status_code=status_code, detail=detail)


class ResourceExistsException(ExtendedHTTPException):
    """Raised whenever there is an attempt to create instance that does not match UNIQUE constraint"""

    def __init__(self, status_code: Optional[int] = status.HTTP_409_CONFLICT, detail: Optional[str] = None):
        status_code = status_code or status.HTTP_409_CONFLICT
        detail = detail or (
            "Resource you are trying to create either already exists "
            "or another resource exists that matches your resource's signature"
        )
        super().__init__(status_code=status_code, detail=detail)


class InvalidOperation(ExtendedHTTPException):
    """Raised whenever there was an attempt to do something that doesn't make any sense"""

    def __init__(self, status_code: Optional[int] = status.HTTP_400_BAD_REQUEST, detail: Optional[str] = None):
        status_code = status_code or status.HTTP_400_BAD_REQUEST
        detail = detail or "The action you are trying to perform does not make sense in the current context"
        super().__init__(status_code=status_code, detail=detail)


class InsufficientPermissions(ExtendedHTTPException):
    """Raised whenever somebody attempts to do something they are not allowed to"""

    def __init__(self, required: Optional[str] = None):
        required = required or "unknown"
        detail = f"You do not have sufficent permissions to perform this action. You need '{required}' permission."
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class CredentialsExpired(ExtendedHTTPException):
    """Raised when credentials in token expire"""

    def __init__(self):
        super().__init__(status_code=HTTP_401_UNAUTHORIZED, detail="Credentials expired")


class ResourceNotFound(ExtendedHTTPException):
    """Raised when specified resource was not found"""

    def __init__(self, res_type: str = "resource", res_name: Optional[str] = None):
        status_code = status.HTTP_404_NOT_FOUND
        detail = f"Specified {res_type} ({res_name}) was not found"
        super().__init__(status_code=status_code, detail=detail)
