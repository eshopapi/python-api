"""API schemas without relation to DB
"""

from typing import List, Optional
from pydantic import BaseModel, EmailStr, constr  # pylint: disable=no-name-in-module

from shopapi.constants import PASSWORD_REGEX, ROLE_PUBLIC_ID
from shopapi.helpers import security
from shopapi.schemas.base import ComputedBase, ORMBase


class LoginUserIn(ComputedBase):
    """Model for user login input"""

    email: EmailStr
    password: constr(strip_whitespace=True, min_length=6, regex=PASSWORD_REGEX)  # type: ignore

    @property
    def password_hash(self) -> bytes:
        """Bcrypt password hash"""
        return security.get_password_hash(self.password)

    @staticmethod
    def get_computed_properties() -> List[str]:
        return ["password_hash"]


class RegisterUserIn(BaseModel):
    """Model for user to register"""

    email: EmailStr
    password_hash: bytes
    role_id: int = ROLE_PUBLIC_ID

    @staticmethod
    def from_plain(plain_user: LoginUserIn) -> "RegisterUserIn":
        """Creates `RegisterUserIn` instance from `LoginUserIn` instance.
        It basically only hashes the password
        """
        phash = security.get_password_hash(plain_user.password)
        return RegisterUserIn(email=plain_user.email, password_hash=phash)


class RoleUpdateIn(BaseModel):
    """Model for changing user's role"""

    role_id: int
    user_id: int


class RoleUpdateOut(ORMBase):
    """Model for returning user's changed role"""

    role_id: int
    id: int
    email: EmailStr


class UserUpdateIn(ComputedBase):
    """Model for changing user's data"""

    password: Optional[str]
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    picture: Optional[str]

    @property
    def password_hash(self) -> Optional[bytes]:
        """Compute password hash"""
        if self.password is None:
            return None
        return security.get_password_hash(self.password)

    @staticmethod
    def get_computed_properties() -> List[str]:
        return ["password_hash"]


class UserUpdateOut(ORMBase):
    """Model after changing user's data"""

    id: int
    role_id: int
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    picture: Optional[str]
