"""Roles routes
"""

from typing import List
from fastapi import APIRouter, Depends

from shopapi import actions
from shopapi.helpers import dependencies as deps
from shopapi.schemas import schemas

router = APIRouter(prefix="/role", tags=["Roles"], dependencies=[Depends(deps.get_user)])

operator = actions.role.RoleOperator()


@router.get("/", response_model=List[schemas.Role])
async def role_list(
    role: schemas.Role = Depends(deps.get_user_role), common: deps.QueryParams = Depends(deps.query_params)
):
    """List all roles

    Required permissions:

        - `roles.read`
    """
    return await operator.list(common, role)


@router.get("/{role_id}", response_model=schemas.Role)
async def role_get(role_id: int, role: schemas.Role = Depends(deps.get_user_role)):
    """Get role details

    Required permissions:

        - `roles.read`
    """
    return await operator.get(role_id, role)


@router.post("/", response_model=schemas.Role)
async def role_create(role_data: schemas.RoleInputUser, role: schemas.Role = Depends(deps.get_user_role)):
    """Create role

    Required permissions:

        - `roles.write`
    """
    return await operator.create(role_data, role)


@router.put("/{role_id}", response_model=schemas.Role)
async def role_update(
    role_id: int, role_data: schemas.RoleInputUser, role: schemas.Role = Depends(deps.get_user_role)
):
    """Update role details

    Required permissions:

        - `roles.write`
    """
    return await operator.update(role_id, role_data, role)


@router.delete("/{role_id}")
async def role_delete(role_id: int, role: schemas.Role = Depends(deps.get_user_role)):
    """Delete role from database

    Required permissions:

        - `roles.delete`
    """
    await operator.delete(role_id, role)
    return {"detail": "Removed"}
