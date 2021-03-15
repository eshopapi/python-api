"""Exceptions"""

from typing import Optional
from fastapi import HTTPException, status

from shopapi.config import Config


class UnexpectedException(HTTPException):
    """Raised whenever an unexpected error ocurrs. Displays support contact to the user."""

    def __init__(
        self, status_code: Optional[int] = status.HTTP_500_INTERNAL_SERVER_ERROR, detail: Optional[str] = None
    ):
        status_code = status_code or status.HTTP_500_INTERNAL_SERVER_ERROR
        detail = detail or f"Unexpected error ocurred. Please contact us at {Config.support_contact}."
        super().__init__(status_code=status_code, detail=detail)


class LoginError(HTTPException):
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


class UserAlreadyExists(HTTPException):
    """Raised when user is about to register but his email already exists"""

    def __init__(self, email: Optional[str] = None):
        detail = f"User with specified e-mail ({email}) already exists"
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class CredentialsException(HTTPException):
    """Raised when credentials provided by the user cannot be verified"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthenticationException(HTTPException):
    """Raised when the user could not be authenticated"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


class SecurityException(HTTPException):
    """Raised when a suspection that someone is trying to do something ugly rises"""

    def __init__(self, status_code: Optional[int] = status.HTTP_401_UNAUTHORIZED, detail: Optional[str] = None):
        status_code = status_code or status.HTTP_401_UNAUTHORIZED
        detail = detail or (
            "Security error was raised, this may happen when something unexpected ocurrs, "
            "that looks like someone is trying to access something they are not allowed to"
        )
        super().__init__(status_code=status_code, detail=detail)


class ResourceExistsException(HTTPException):
    """Raised whenever there is an attempt to create instance that does not match UNIQUE constraint"""

    def __init__(self, status_code: Optional[int] = status.HTTP_409_CONFLICT, detail: Optional[str] = None):
        status_code = status_code or status.HTTP_409_CONFLICT
        detail = detail or (
            "Resource you are trying to create either already exists "
            "or another resource exists that matches your resource's signature"
        )
        super().__init__(status_code=status_code, detail=detail)
