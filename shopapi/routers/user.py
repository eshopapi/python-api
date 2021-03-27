"""User-related API endpoints
"""

import logging
from typing import List
from fastapi import APIRouter, Depends
from shopapi.helpers import dependencies as deps, exceptions
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
    return await operator.list(common, role)


@router.get("/{user_id}", response_model=api.UserUpdateOut)
async def user_get(
    user_id: int, user: schemas.UserToken = Depends(deps.get_user), role: schemas.Role = Depends(deps.get_user_role)
):
    """Get user info

    Required permissions:

        - `users.read`
    """
    if user.id == user_id:
        return await operator.get(user_id)
    return await operator.get(user_id, role)


@router.post("/")
async def user_create(user: api.UserUpdateIn, role: schemas.Role = Depends(deps.get_user_role)):
    """Create a user

    Required permissions:

        - `users.write`
    """
    return await operator.create(user, role)


@router.delete("/{user_id}", dependencies=[Depends(deps.get_user)])
async def user_delete(user_id: int, role: schemas.Role = Depends(deps.get_user_role)):
    """Delete user.

    Required permissions:

        - `users.delete`
    """
    return await operator.delete(user_id, role)


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
    if user.id == user_id:
        logger.info("Skipping role check, user editing themselves")
        return await operator.update(user_id, info)
    return await operator.update(user_id, info, role)
