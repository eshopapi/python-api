"""Category endpoints
"""

from typing import List
from fastapi import APIRouter, Depends

from shopapi import actions
from shopapi.schemas import schemas, models
from shopapi.helpers import dependencies as deps, exceptions

router = APIRouter(prefix="/category", tags=["Categories"])

operator = actions.category.CategoryOperator()


@router.get("/", response_model=List[schemas.Category])
async def category_list(common: deps.QueryParams = Depends(deps.query_params)):
    """List all categories"""
    return await operator.list(common)


@router.get("/{category_id}", response_model=schemas.Category)
async def category_get(category_id: int, role: schemas.Role = Depends(deps.get_user_role)):
    """Get category details by category id

    Required permissions:

        - `categories.read`
    """
    return await operator.get(category_id, role)


@router.post("/", response_model=schemas.Category)
async def category_create(category: schemas.CategoryUserInput, role: schemas.Role = Depends(deps.get_user_role)):
    """Create category

    Required permissions:

        - `categories.write`
    """
    return await operator.create(category, role)


@router.put("/{category_id}", response_model=schemas.Category)
async def category_update(
    category_id: int, category: schemas.CategoryUserInput, role: schemas.Role = Depends(deps.get_user_role)
):
    """Update category details

    Required permissions:

        - `categories.write`
    """
    return await operator.update(category_id, category, role)


@router.delete("/{category_id}")
async def category_delete(category_id: int, role: schemas.Role = Depends(deps.get_user_role)):
    """Delete category from database

    Required permissions:

        - `categories.delete`
    """
    await operator.delete(category_id, role)
    return {"detail": "Removed"}


@router.get("/{category_id}/tag", response_model=List[schemas.Tag])
async def category_tags_list(category_id: int, role: schemas.Role = Depends(deps.get_user_role)):
    """List category's tags from database

    Required permissions:

        - `categories.read`
    """
    category_db = await operator.mget(category_id, role)
    # this is because of mypy
    # how do I make mypy know that models.Category is indeed a subclass
    # of BaseModelTortoise and can be returned?
    if isinstance(category_db, models.Category):
        return [schemas.Tag.from_orm(tag) for tag in category_db.tags]


@router.put("/{category_id}/tag/{tag_id}", response_model=List[schemas.Tag])
async def category_tags_add(category_id: int, tag_id: int, role: schemas.Role = Depends(deps.get_user_role)):
    """Add tag to category.

    Required permissions:

        - `categories.write`
    """
    return await operator.add_related(category_id, tag_id, "tags", role)


@router.delete("/{category_id}/tag/{tag_id}", response_model=List[schemas.Tag])
async def category_tags_delete(category_id: int, tag_id: int, role: schemas.Role = Depends(deps.get_user_role)):
    """Delete tag from category

    Required permissions:

        - `categories.write`
    """
    return await operator.remove_related(category_id, tag_id, "tags", role)
