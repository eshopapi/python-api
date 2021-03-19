"""API schemas without relation to DB
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, constr  # pylint: disable=no-name-in-module

from shopapi.constants import PASSWORD_REGEX, ROLE_PUBLIC_ID
from shopapi.helpers import security


class ORMBase(BaseModel):
    """Base for orm-mode schemas"""

    class Config:
        """Class metadata"""

        orm_mode = True


class LoginUserIn(BaseModel):
    """Model for user login input"""

    email: EmailStr
    password: constr(strip_whitespace=True, min_length=6, regex=PASSWORD_REGEX)  # type: ignore


class RegisterUserIn(BaseModel):
    """Model for user to register"""

    email: EmailStr
    password: bytes
    role_id: int = ROLE_PUBLIC_ID

    @staticmethod
    def from_plain(plain_user: LoginUserIn) -> "RegisterUserIn":
        """Creates `RegisterUserIn` instance from `LoginUserIn` instance.
        It basically only hashes the password
        """
        phash = security.get_password_hash(plain_user.password)
        return RegisterUserIn(email=plain_user.email, password=phash)


class RoleUpdateIn(BaseModel):
    """Model for changing user's role"""

    role_id: int
    user_id: int


class RoleUpdateOut(ORMBase):
    """Model for returning user's changed role"""

    role_id: int
    id: int
    email: EmailStr


class UserUpdateIn(BaseModel):
    """Model for changing user's data"""

    password: Optional[bytes]
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    picture: Optional[str]


class UserUpdateOut(ORMBase):
    """Model after changing user's data"""

    id: int
    role_id: int
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    picture: Optional[str]
