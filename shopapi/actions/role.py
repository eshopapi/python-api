"""Tag resource crud operator
"""

from shopapi.schemas import schemas, models
from shopapi.actions.base import ResourceOperator


class RoleOperator(ResourceOperator):
    """CRUD operator over Role"""

    resource = "Role"
    model = models.Role
    schema = schemas.Role
    role_name = "roles"
