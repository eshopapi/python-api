"""User-related API endpoints
"""

from fastapi import APIRouter, Depends
from shopapi.helpers import dependencies
from shopapi.schemas import schemas

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me")
async def user_info(user: schemas.UserToken = Depends(dependencies.get_user)):
    """Return user information"""
    return user
