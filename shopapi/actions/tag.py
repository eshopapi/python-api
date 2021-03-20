"""Tag resource crud operator
"""

from shopapi.schemas import schemas, models
from shopapi.actions.base import ResourceOperator


class TagOperator(ResourceOperator):
    """CRUD operator over Tag"""

    resource = "Tag"
    model = models.Tag
    schema = schemas.Tag
    role_name = "tags"
