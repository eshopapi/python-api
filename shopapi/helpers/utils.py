"""Utility helpers
"""

from typing import Optional, Type, Union
from tortoise.queryset import Q

from shopapi.schemas import models
from shopapi.helpers.dependencies import QueryParams


def build_search_query(search: Union[Optional[str], Optional[QueryParams]], model: Type[models.BaseModel]) -> Q:
    """Build search query from either str search or `QueryParams` object holding the search string.
    Returns empty query if search is None
    """
    if isinstance(search, QueryParams):
        search = search.search
    if search is None:
        return Q()
    query = Q(*[Q(**{f"{field}__icontains": search}) for field in model.get_search_fields()], join_type="OR")
    return query
