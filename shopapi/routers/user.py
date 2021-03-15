"""User-related API endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, status, Cookie
from shopapi.helpers import dependencies, exceptions
from shopapi.schemas import models, schemas, api
from shopapi import actions

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=schemas.UserToken)
async def user_info(user: schemas.UserToken = Depends(dependencies.get_user)):
    """Return user information"""
    return user


@router.post("/")
async def user_create(user: api.LoginUserIn, redirect_to: Optional[str] = Cookie(None)):
    """Register new user"""
    if await actions.user.user_email_exists(user.email):
        raise exceptions.UserAlreadyExists(user.email)
    if await actions.user.openid_email_exists(user.email):
        raise exceptions.LoginReusedEmailError(user.email)
    reg_user = api.RegisterUserIn.from_plain(user)
    user_model = await models.User.create(**reg_user.dict())
    userdb = schemas.UserFromDB.from_orm(user_model)
    response = await actions.user.login_user(userdb, redirect_to=redirect_to)
    response.status_code = status.HTTP_201_CREATED
    return response
