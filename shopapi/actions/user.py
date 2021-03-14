"""User-specific actions
"""

import logging

from datetime import timedelta
from typing import Optional
from starlette.responses import JSONResponse, RedirectResponse, Response

from shopapi.schemas import schemas, models
from shopapi.helpers import exceptions, security
from shopapi.config import Config

logger = logging.getLogger(__name__)


async def load_openid(openid: schemas.OpenID) -> Optional[schemas.OpenIDFromDB]:
    """Load OpenID from db"""
    oid = await models.OpenID.filter(
        email=openid.email, provider=openid.provider, provider_id=openid.provider_id
    ).first()
    if not oid:
        return None
    return schemas.OpenIDFromDB.from_orm(oid)


async def get_user_by_openid(openid: schemas.OpenID) -> Optional[schemas.UserFromDB]:
    """Get user matching openid in the database"""
    oid = await load_openid(openid)
    if oid is None:
        return None
    user = await models.User.get(id=oid.user_id)
    if user:
        return schemas.UserFromDB.from_orm(user)


async def get_or_create_user(openid: schemas.OpenID) -> schemas.UserFromDB:
    """Get user from database based on openid provider information.
    If the user does not exist, it is created first
    """
    user = await get_user_by_openid(openid)
    if user:
        return user
    if await load_openid(openid):
        # The user has already tried logging in using this provider
        # but the user was not created in the db
        logger.error(openid)
        raise exceptions.UnexpectedException()
    openids_count = await models.OpenID.filter(email=openid.email).count()
    user_exists = await models.User.filter(email=openid.email).exists()
    logger.info("count: %d, exists: %s", openids_count, user_exists)
    if user_exists or openids_count:
        raise exceptions.LoginReusedEmailError(openid.email)
    user = schemas.UserDBInput(
        email=openid.email, first_name=openid.first_name, last_name=openid.last_name, picture=openid.picture
    )
    user_db = await models.User.create(**user.dict(exclude_none=True))
    await models.OpenID.create(**openid.dict(exclude_none=True), user_id=user_db.id)
    return schemas.UserFromDB.from_orm(user_db)


async def login_user(
    user: schemas.UserFromDB,
    permanent: bool = False,
    redirect_to: Optional[str] = None,
    openid: Optional[schemas.OpenID] = None,
) -> Response:
    """Create access token and return response with cookie with the token in it"""
    if permanent:
        expires = timedelta(days=90)
    else:
        expires = timedelta(minutes=Config.access_token_expire)
    token = security.create_access_token(user, expires, openid)
    if redirect_to:
        if not redirect_to.startswith(Config.base_url):
            logger.warning(
                "User %s was being redirected to %s which is not in the root domain "
                "and so the attempt was not permitted and user will be redirected to %s instead",
                user.email,
                redirect_to,
                Config.base_url,
            )
            redirect_to = Config.base_url
        response = RedirectResponse(url=redirect_to)
    else:
        response = JSONResponse({"user_id": user.id, "email": user.email, "token": token})
    expires_seconds = int(expires.total_seconds())
    response.set_cookie("sessiontoken", token, max_age=expires_seconds, expires=expires_seconds)
    return response


async def user_add_openid(openid: schemas.OpenID, user_id: int):
    """Add another openid for existing user"""
    openid.user_id = user_id
    if await models.OpenID.filter(provider=openid.provider, provider_id=openid.provider_id).exists():
        raise exceptions.ResourceExistsException()
    await models.OpenID.create(**openid.dict(exclude_none=True))