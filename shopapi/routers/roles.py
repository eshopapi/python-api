"""Roles routes
"""

from typing import List
from fastapi import APIRouter, Depends
from tortoise.exceptions import DoesNotExist, IntegrityError

from shopapi import constants
from shopapi.helpers import dependencies as deps, exceptions, utils
from shopapi.schemas import models, schemas

router = APIRouter(prefix="/role", tags=["Roles"], dependencies=[Depends(deps.get_user)])


@router.get("/", response_model=List[schemas.Role])
async def role_list(
    role: schemas.Role = Depends(deps.get_user_role), common: deps.QueryParams = Depends(deps.query_params)
):
    """List all roles

    Required permissions:

        - `roles.read`
    """
    if not role.roles.read:
        raise exceptions.InsufficientPermissions("roles.read")
    query = utils.build_search_query(common, models.Role)
    roles = await models.Role.filter(query).limit(common.limit).offset(common.offset)
    return [schemas.Role.from_orm(role_db) for role_db in roles]


@router.get("/{role_id}", response_model=schemas.Role)
async def role_get(role_id: int, role: schemas.Role = Depends(deps.get_user_role)):
    """Get role details

    Required permissions:

        - `roles.read`
    """
    if not role.roles.read:
        raise exceptions.InsufficientPermissions("roles.read")
    try:
        role_db = await models.Role.get(id=role_id)
    except DoesNotExist:
        raise exceptions.ResourceNotFound("role", role_id)
    return schemas.Role.from_orm(role_db)


@router.post("/", response_model=schemas.Role)
async def role_create(role_data: schemas.RoleInputUser, role: schemas.Role = Depends(deps.get_user_role)):
    """Create role

    Required permissions:

        - `roles.write`
    """
    if not role.roles.write:
        raise exceptions.InsufficientPermissions("roles.write")
    try:
        role_db = await models.Role.create(**role_data.dict(exclude_none=True))
        return schemas.Role.from_orm(role_db)
    except IntegrityError:
        raise exceptions.ResourceExistsException(detail=f"Role already exists with title {role_data.title}")


@router.put("/{role_id}", response_model=schemas.Role)
async def role_update(
    role_id: int, role_data: schemas.RoleInputUser, role: schemas.Role = Depends(deps.get_user_role)
):
    """Update role details

    Required permissions:

        - `roles.write`
    """
    if not role.roles.write:
        raise exceptions.InsufficientPermissions("roles.write")
    try:
        role_db = await models.Role.get(id=role_id)
    except DoesNotExist:
        raise exceptions.ResourceNotFound("role", role_id)
    try:
        await role_db.update_from_dict(role_data.dict(exclude_none=True))
        await role_db.save()
        return schemas.Role.from_orm(role_db)
    except IntegrityError:
        raise exceptions.ResourceExistsException(detail=f"Role already exists with title {role_data.title}")


@router.delete("/{role_id}")
async def role_delete(role_id: int, role: schemas.Role = Depends(deps.get_user_role)):
    """Delete role from database

    Required permissions:

        - `roles.delete`
    """
    if not role.roles.delete:
        raise exceptions.InsufficientPermissions("roles.delete")
    if role_id in constants.DEFAULT_ROLES:
        raise exceptions.InvalidOperation(detail="Default roles cannot be removed")
    try:
        role_db = await models.Role.get(id=role_id)
        await role_db.delete()
    except DoesNotExist:
        raise exceptions.ResourceNotFound("role", role_id)
    return {"detail": "Removed"}
