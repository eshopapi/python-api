"""Tag endpoints
"""

from typing import List
from fastapi import APIRouter, Depends

from shopapi import actions
from shopapi.schemas import schemas
from shopapi.helpers import dependencies as deps

router = APIRouter(prefix="/tag", tags=["Tags"])

operator = actions.tag.TagOperator()


@router.get("/", response_model=List[schemas.Tag])
async def tag_list(common: deps.QueryParams = Depends(deps.query_params)):
    """List all tags"""
    return await operator.list(common)


@router.get("/{tag_id}", response_model=schemas.Tag)
async def tag_get(
    tag_id: int,
    role: schemas.Role = Depends(deps.get_user_role),
):
    """Get tag details by tag id

    Required permissions:

        - `tags.read`
    """
    return await operator.get(tag_id, role)


@router.post("/", response_model=schemas.Tag)
async def tag_create(tag: schemas.TagUserInput, role: schemas.Role = Depends(deps.get_user_role)):
    """Create tag

    Required permissions:

        - `tags.write`
    """
    return await operator.create(tag, role)


@router.put("/{tag_id}", response_model=schemas.Tag)
async def tag_update(tag_id: int, tag: schemas.TagUserInput, role: schemas.Role = Depends(deps.get_user_role)):
    """Update tag details

    Required permissions:

        - `tags.write`
    """
    return await operator.update(tag_id, tag, role)


@router.delete("/{tag_id}")
async def tag_delete(tag_id: int, role: schemas.Role = Depends(deps.get_user_role)):
    """Delete tag from database

    Required permissions:

        - `tags.delete`
    """
    await operator.delete(tag_id, role)
    return {"detail": "Removed"}
