"""Security helpers
"""

import logging
from datetime import datetime, timedelta
from typing import Mapping, Optional

from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from tortoise.exceptions import DoesNotExist

from shopapi.schemas import schemas, models
from shopapi import constants
from shopapi.helpers import exceptions
from shopapi.config import Config

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(pwd_test: str, pwd_hash: str) -> bool:
    """Verify input password string with password hash from database

    Returns:
        bool -- True or False whether verified
    """
    return pwd_context.verify(pwd_test, pwd_hash)


def get_password_hash(password: str) -> bytes:
    """Get password string hashed to be saved in db"""
    return pwd_context.hash(password).encode("ascii")


def create_access_token(
    user: schemas.UserFromDB, expires: Optional[timedelta] = None, openid: Optional[schemas.OpenID] = None
) -> str:
    """Create jwt token based on user information.
    Only `id` and `email` fields are actually used to build jwt.
    Optional `expires` specifies when the token expires, otherwise, default is used from config.
    """
    expires = expires or timedelta(minutes=Config.access_token_expire)
    data = {
        "iss": Config.base_url,
        "nbf": datetime.utcnow(),
        "iat": datetime.utcnow(),
        "sub": user.email,
        "sid": user.id,
        "exp": datetime.utcnow() + expires,
        "pvd": openid.provider if openid else "password",
        "pid": openid.provider_id if openid else None,
        "rid": user.role_id,
    }
    jwt_content = jwt.encode(data, Config.secret_key, algorithm=constants.JWT_ALGORITHM)
    return jwt_content


async def decode_jwt(token: str) -> Mapping:
    """Get token info from token"""
    try:
        payload = jwt.decode(token, Config.secret_key, algorithms=[constants.JWT_ALGORITHM])
        expires = datetime.fromtimestamp(float(payload.get("exp", 0)))
        not_before = datetime.fromtimestamp(float(payload.get("nbf", 0)))
        now = datetime.utcnow()
        if expires < now:
            logger.info("Expired token: %s, expires: %s", payload, expires)
            raise exceptions.CredentialsExpired()
        if now < not_before:
            logger.info("Token not valid yet: %s, not-before: %s", payload, not_before)
            raise exceptions.CredentialsException()
        sid: Optional[int] = payload.get("sid")
        if sid is None:
            raise exceptions.CredentialsException()
        try:
            user_db = await models.User.get(id=sid)
        except DoesNotExist as error:
            logger.warning("Someone is probably trying to login with a non-existing account")
            logger.warning(error)
            logger.warning(payload)
            raise exceptions.CredentialsException()
        rid: Optional[int] = payload.get("rid")
        if rid is None:
            raise exceptions.CredentialsException()
        if rid != (await user_db.role).id:
            raise exceptions.CredentialsExpired()
        return payload
    except JWTError as error:
        logger.error(error)
        raise exceptions.CredentialsException()


async def user_from_jwt(token: str) -> schemas.UserFromDB:
    """Get user object from jwt token

    Arguments:
        token {str} -- JWT token

    Raises:
        exceptions.CredentialsException: If the token is missing,
            invalid or the user specified within does not exist

    Returns:
        models.User -- User from DB
    """
    payload = await decode_jwt(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise exceptions.CredentialsException()
    user = await models.User.get(user_id)
    if user is None:
        raise exceptions.CredentialsException()
    return schemas.UserFromDB.from_orm(user)
