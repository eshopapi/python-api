"""Dependencies to make our lifes easier and our views cleaner"""

from typing import Optional
from fastapi import Cookie, Header, Depends

from shopapi.config import Config
from shopapi.helpers import exceptions, security
from shopapi.schemas import schemas, models


async def get_user_token(
    token: Optional[str] = None,
    x_token: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    sessiontoken: Optional[str] = Cookie(None),
) -> Optional[str]:
    """FastAPI dependency to get token from wherever it may be hiding"""
    if token:
        return token
    if x_token:
        return x_token
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    if sessiontoken:
        return sessiontoken
    return None


async def get_user_token_strict(token: Optional[str] = Depends(get_user_token)) -> str:
    """FastAPI dependency to get token from wherever it may be hiding.
    Raises error if no token is found"""
    if token:
        return token
    raise exceptions.AuthenticationException()


async def get_user(token: str = Depends(get_user_token_strict)) -> schemas.UserToken:
    """Get user information schema from the decoded token info"""
    token_info = await security.decode_jwt(token)
    return schemas.UserToken.from_token(token_info)


async def get_user_role(user: schemas.UserToken = Depends(get_user)) -> schemas.Role:
    """Get user's role"""
    role_db = await models.Role.get(id=user.role_id)
    if not role_db:
        raise exceptions.UnexpectedException(
            detail=f"We were unable to retrieve your user information. Please contact us at {Config.support_contact}"
        )
    return schemas.Role.from_orm(role_db)
