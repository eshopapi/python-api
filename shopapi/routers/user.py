"""User-related API endpoints
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Cookie
from starlette.responses import JSONResponse
from tortoise.exceptions import ConfigurationError, DoesNotExist
from shopapi.helpers import dependencies as deps, exceptions, security, utils
from shopapi.schemas import models, schemas, api
from shopapi import actions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["Users"])

operator = actions.user.UserOperator()


@router.get("/me", response_model=schemas.UserToken)
async def user_info(user: schemas.UserToken = Depends(deps.get_user)):
    """Return user information"""
    return user


@router.get("/role", response_model=schemas.Role, dependencies=[Depends(deps.get_user)])
async def user_role(role: schemas.Role = Depends(deps.get_user_role)):
    """Get user's role and return it"""
    return role


@router.put("/role", dependencies=[Depends(deps.get_user)], response_model=api.RoleUpdateOut)
async def user_role_update(role_update: api.RoleUpdateIn, role: schemas.Role = Depends(deps.get_user_role)):
    """Update user's role.

    Required permissions:

        - `users.write`
        - `roles.write`
    """
    if not role.users.write or not role.roles.write:
        raise exceptions.InsufficientPermissions("users.write, roles.write")
    if not await models.Role.get(id=role_update.role_id):
        raise exceptions.ResourceNotFound("role", role_update.role_id)
    if not (user_db := await models.User.get(id=role_update.user_id)):
        raise exceptions.ResourceNotFound("user", role_update.user_id)
    user_db = await user_db.update_from_dict({"role_id": role_update.role_id})
    await user_db.save()
    await user_db.fetch_related("role")
    return api.RoleUpdateOut.from_orm(user_db)


@router.get(
    "/",
    dependencies=[Depends(deps.get_user)],
    response_model=List[api.UserUpdateOut],
)
async def user_list(
    role: schemas.Role = Depends(deps.get_user_role),
    common: deps.QueryParams = Depends(deps.query_params),
):
    """List all users

    Required permissions:

        - `users.read`
    """
    if not role.users.read:
        raise exceptions.InsufficientPermissions("users.read")
    query = utils.build_search_query(common, models.User)
    users = await models.User.filter(query).limit(common.limit).offset(common.offset)
    return [api.UserUpdateOut.from_orm(user) for user in users]


@router.get("/{user_id}", response_model=api.UserUpdateOut)
async def user_get(
    user_id: int, user: schemas.UserToken = Depends(deps.get_user), role: schemas.Role = Depends(deps.get_user_role)
):
    """Get user info

    Required permissions:

        - `users.read`
    """
    if not role.users.read and user.id != user_id:
        raise exceptions.InsufficientPermissions("users.read")
    try:
        found = await models.User.get(id=user_id)
    except DoesNotExist:
        raise exceptions.ResourceNotFound("user", user_id)
    return api.UserUpdateOut.from_orm(found)


@router.post("/")
async def user_create(user: api.LoginUserIn, redirect_to: Optional[str] = Cookie(None)):
    """Register new user"""
    userdb = await actions.user.create_user(user)
    response = await actions.user.login_user(userdb, redirect_to=redirect_to)
    response.status_code = status.HTTP_201_CREATED
    return response


@router.delete("/{user_id}")
async def user_delete(
    user_id: int, user: schemas.UserToken = Depends(deps.get_user), role: schemas.Role = Depends(deps.get_user_role)
):
    """Delete user.
    Only works if current user is deleting themselves or they have users.DELETE

    Required permissions:

        - `users.delete`
    """
    if user.id != user_id and not role.users.delete:
        raise exceptions.InsufficientPermissions("users.delete")
    await actions.user.user_delete(user_id)
    response = JSONResponse(f"User {user_id} was deleted from the database")
    if user.id == user_id:
        response.delete_cookie("sessiontoken")
    return response


@router.put("/{user_id}", response_model=api.UserUpdateOut)
async def user_update(
    user_id: int,
    info: api.UserUpdateIn,
    user: schemas.UserToken = Depends(deps.get_user),
    role: schemas.Role = Depends(deps.get_user_role),
):
    """Update user in database specified with `user_id` with the data in `info`

    Required permissions:

        - `users.write`
    """
    if user.id != user_id and not role.users.write:
        raise exceptions.InsufficientPermissions("users.write")
    user_db = await models.User.get(id=user_id)
    if not user_db:
        raise exceptions.ResourceNotFound("user", user_id)
    try:
        dct = info.dict(exclude_none=True)
        password = dct.pop("password", None)
        if password is not None:
            dct["password"] = security.get_password_hash(password)
        user_db = await user_db.update_from_dict(dct)
        await user_db.save()
        return api.UserUpdateOut.from_orm(user_db)
    except ValueError as error:
        logger.error(error)
        raise exceptions.InvalidOperation()
    except ConfigurationError as error:
        logger.error(error)
        raise exceptions.UnexpectedException()
