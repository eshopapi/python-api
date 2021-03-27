"""Tag resource crud operator
"""

from shopapi.schemas import schemas, models
from shopapi.schemas.base import ModelDefinition
from shopapi.actions.base import ResourceOperator


class CategoryOperator(ResourceOperator):
    """CRUD operator over Category"""

    resource = "Category"
    model = models.Category
    schema = schemas.Category
    role_name = "categories"
    related_fields = {
        "tags": ModelDefinition(models.Tag, schemas.Tag),
        "parent_category": ModelDefinition(models.Category, schemas.Category),
    }
