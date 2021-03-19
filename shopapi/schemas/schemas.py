"""Schemas used throughout the API with connection to DB
"""

from datetime import datetime
from enum import IntFlag
from typing import Mapping, Optional, Union

from pydantic import BaseModel, EmailStr  # pylint: disable=no-name-in-module
from fastapi_sso.sso.base import OpenID as OpenIDSSO

from shopapi import constants

class ORMModel(BaseModel):
    """Base for orm models"""

    class Config:
        """Metadata"""

        orm_mode = True


class Permission(IntFlag):
    """Basic policies applicable to all resources"""

    READ = 1
    WRITE = 2
    DELETE = 4

    @property
    def read(self) -> bool:
        """Returns True if current permission contains READ permissions"""
        return bool(self & Permission.READ)

    @property
    def write(self) -> bool:
        """Returns True if current permission contains WRITE permissions"""
        return bool(self & Permission.WRITE)

    @property
    def delete(self) -> bool:
        """Returns True if current permission contains DELETE permissions"""
        return bool(self & Permission.DELETE)


ADMIN = Permission.READ | Permission.WRITE | Permission.DELETE
EDITOR = Permission.READ | Permission.WRITE
VIEWER = Permission.READ

class RoleInput(ORMModel):
    """Class to contain policies"""

    id: Optional[int]
    title: str

    users: Permission = Permission(0)
    roles: Permission = Permission(0)


class Role(RoleInput):
    """Class to return roles from db"""

    id: int


class UserDBInput(ORMModel):
    """User input to be loaded into DB"""

    id: Optional[int]
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    picture: Optional[str]
    password: Optional[bytes]
    role_id: Optional[int] = constants.ROLE_PUBLIC_ID
    role: Optional[Role] = None


class OpenID(BaseModel):
    """OpenID as returned from SSO provider"""

    id: Optional[int]
    user_id: Optional[int]
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: Optional[str]
    picture: Optional[str]
    provider: str
    provider_id: str

    @staticmethod
    def from_sso(openidsso: OpenIDSSO) -> "OpenID":
        """Return OpenID object from OpenID object returned with fastapi_sso"""
        dct = openidsso.dict()
        dct["provider_id"] = dct["id"]
        del dct["id"]
        return OpenID(**dct)


class OpenIDFromDB(ORMModel, OpenID):
    """OpenID"""

    id: int


class UserFromDB(UserDBInput):
    """UserFromDB"""

    id: int


class UserToken(BaseModel):
    """User as returned from token"""

    id: int
    email: EmailStr
    issuer: str
    not_before: datetime
    issued_at: datetime
    expires: datetime
    provider: str
    provider_id: Optional[str]
    role_id: int

    @staticmethod
    def from_token(token_info: Union[Mapping, dict]) -> "UserToken":
        """Return `UserToken` object from `token_info` mapping"""
        return UserToken(
            id=token_info.get("sid"),
            email=token_info.get("sub"),
            issuer=token_info.get("iss"),
            not_before=token_info.get("nbf"),
            issued_at=token_info.get("iat"),
            expires=token_info.get("exp"),
            provider=token_info.get("pvd"),
            provider_id=token_info.get("pid"),
            role_id=token_info.get("rid"),
        )
