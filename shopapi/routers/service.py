"""Service endpoints used to migrate db, update, backup etc.
"""

import logging
from typing import List
from fastapi import APIRouter
from tortoise.exceptions import DoesNotExist
from shopapi import actions
from shopapi.helpers import exceptions
from shopapi.schemas import schemas, models
from shopapi.schemas.schemas import (
    ADMIN,
    EDITOR,
    VIEWER,
)

from shopapi.constants import ROLE_ADMIN_ID, ROLE_EDITOR_ID, ROLE_PUBLIC_ID, ROLE_VIEWER_ID
from shopapi.helpers import demo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/service", tags=["Service"])

default_roles: List[schemas.RoleInput] = [
    schemas.RoleInput(
        id=ROLE_ADMIN_ID, title="admin", users=ADMIN, roles=ADMIN, tags=ADMIN, categories=ADMIN, products=ADMIN
    ),
    schemas.RoleInput(id=ROLE_PUBLIC_ID, title="public"),
    schemas.RoleInput(
        id=ROLE_EDITOR_ID, title="editor", users=EDITOR, roles=EDITOR, tags=EDITOR, categories=EDITOR, products=EDITOR
    ),
    schemas.RoleInput(
        id=ROLE_VIEWER_ID, title="viewer", users=VIEWER, roles=VIEWER, tags=VIEWER, categories=VIEWER, products=VIEWER
    ),
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


@router.get("/demo-data")
async def service_demo_data():
    """Insert demo data"""
    if await models.Shop.is_production():
        raise exceptions.InvalidOperation(detail="The shop is in production mode, this is not doable.")
    for plain_user in demo.users:
        await actions.user.create_user(plain_user)
    for tag_input in demo.tags:
        await models.Tag.create(**tag_input.dict(exclude_none=True))
    for category in demo.categories:
        logger.info("Creating category %s", category)
        await models.Category.create(**category.dict(exclude_none=True, exclude={"category": ["parent_category_id"]}))


@router.delete("/demo-data")
async def service_demo_data_delete():
    """Delete demo data"""
    if await models.Shop.is_production():
        raise exceptions.InvalidOperation(detail="The shop is in production mode, this is not doable.")
    for plain_user in demo.users:
        try:
            user_db = await models.User.get(email=plain_user.email)
            await user_db.delete()
        except DoesNotExist:
            continue
    for tag_input in demo.tags:
        try:
            tag_db = await models.Tag.get(name=tag_input.name)
            await tag_db.delete()
        except DoesNotExist:
            continue
    for category in demo.categories:
        try:
            category_db = await models.Category.get(title=category.title)
            await category_db.delete()
        except DoesNotExist:
            continue
