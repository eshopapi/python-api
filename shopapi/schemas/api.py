"""API schemas

Defined below are schemas used to input / output data to / form various API endpoints.
These schemas have no model counterpart as they are not to be stored in the DB.
"""

from pydantic import BaseModel, EmailStr, constr  # pylint: disable=no-name-in-module

from shopapi.constants import PASSWORD_REGEX
from shopapi.helpers import security


class LoginUserIn(BaseModel):
    """Model for user login input"""

    email: EmailStr
    password: constr(strip_whitespace=True, min_length=6, regex=PASSWORD_REGEX)  # type: ignore


class RegisterUserIn(BaseModel):
    """Model for user to register"""

    email: EmailStr
    password: bytes

    @staticmethod
    def from_plain(plain_user: LoginUserIn) -> "RegisterUserIn":
        """Creates `RegisterUserIn` instance from `LoginUserIn` instance.
        It basically only hashes the password
        """
        phash = security.get_password_hash(plain_user.password)
        return RegisterUserIn(email=plain_user.email, password=phash)
