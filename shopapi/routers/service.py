"""Service endpoints used to migrate db, update, backup etc.
"""

from typing import List
from fastapi import APIRouter
from shopapi.helpers import exceptions
from shopapi.schemas import schemas, models
from shopapi.schemas.schemas import (
    ADMIN,
    EDITOR,
    VIEWER,
    ROLE_ADMIN_ID,
    ROLE_EDITOR_ID,
    ROLE_PUBLIC_ID,
    ROLE_VIEWER_ID,
)

router = APIRouter(prefix="/service", tags=["service"])

default_roles: List[schemas.RoleInput] = [
    schemas.RoleInput(id=ROLE_ADMIN_ID, title="admin", users=ADMIN, roles=ADMIN),
    schemas.RoleInput(id=ROLE_PUBLIC_ID, title="public"),
    schemas.RoleInput(id=ROLE_EDITOR_ID, title="editor", users=EDITOR, roles=EDITOR),
    schemas.RoleInput(id=ROLE_VIEWER_ID, title="viewer", users=VIEWER, roles=VIEWER),
]


@router.get("/db-init")
async def service_db_init():
    """Insert initial data to db"""
    if await models.Shop.is_initialized():
        raise exceptions.InvalidOperation(
            detail="The shop was already intitialized. This action can only be performed once."
        )

    for role in default_roles:
        await models.Role.create(**role.dict(exclude_none=True))

    await models.Shop.set_initialized(True)
