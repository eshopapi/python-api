"""Generic actions needed throughout the API to get rid of code repetition
"""

import logging
from typing import Dict, List, Optional, Type, NamedTuple

from tortoise.exceptions import DoesNotExist, IntegrityError

from shopapi.schemas import schemas, base
from shopapi.schemas.base import BaseModelTortoise, ORMBase
from shopapi.helpers import dependencies as deps, exceptions, utils

logger = logging.getLogger(__name__)


class RoleTuple(NamedTuple):
    """NamedTuple containing role type and permission that was split from str"""

    role: str
    permission: str

    @classmethod
    def from_str(cls, data: str) -> "RoleTuple":
        """Create RoleTuple instance from input `data` in form: `role.permission`.
        E.g.: `users.read` or `tags.delete`
        Raises ValueError if the `data` is in wrong format.
        """
        role, permission = data.split(".")
        return cls(role=role, permission=permission)

    def __str__(self):
        return f"{self.role}.{self.permission}"

    def __repr__(self):
        return str(self)


def test_role(role: schemas.Role, required: RoleTuple) -> bool:
    """Returns True if specified `role` conforms with `required` role"""
    if not hasattr(role, required.role):
        raise ValueError(f"No such role type as '{required.role}'")
    permission: schemas.Permission = getattr(role, required.role)
    if not hasattr(permission, required.permission):
        raise ValueError(f"No such permission type as '{required.permission}")
    return getattr(permission, required.permission)


def role_conforms(role: schemas.Role, required_roles: List[RoleTuple]) -> bool:
    """Returns True if specified `role` conforms with all of the specified `required_roles`."""
    for required in required_roles:
        if not test_role(role, required):
            return False
    return True


class ResourceOperator:
    """Class managing basic CRUD operations over resources between user and database"""

    resource: str = NotImplemented
    model: Type[BaseModelTortoise]
    schema: Type[ORMBase]
    role_name: Optional[str] = None
    permissions: Dict[str, List[str]] = {
        "list": ["read"],
        "get": ["read"],
        "create": ["write"],
        "update": ["write"],
        "delete": ["delete"],
    }
    related_fields: Dict[str, base.ModelDefinition] = {}

    def check_roles(self, role: Optional[schemas.Role], operation: Optional[str] = None):
        """Raise `InsufficientPermissions` exception if the current `role`
        is not eligible for specified `operation`
        """
        if self.role_name is None:
            logger.warning("No target role was provided in role check. Skipping check.")
            return
        if not (role and operation):
            logger.warning("No role was provided in role check or operation does not required. Skipping role check.")
            return
        if not operation in self.permissions:
            logger.warning(
                "Operation '%s' is not specified for operator on model '%s'", operation, self.__class__.__name__
            )
            return
        required_roles = [
            RoleTuple(role=self.role_name, permission=permission) for permission in self.permissions[operation]
        ]
        if not role_conforms(role, required_roles):
            raise exceptions.InsufficientPermissions([str(r) for r in required_roles])
        return

    async def mlist(self, common: deps.QueryParams, role: Optional[schemas.Role] = None) -> List[BaseModelTortoise]:
        """List resources and do not convert them to Pydantic"""
        self.check_roles(role, "list")
        query = utils.build_search_query(common, self.model)
        return (
            await self.model.filter(query)
            .prefetch_related(*self.related_fields)
            .limit(common.limit)
            .offset(common.offset)
        )

    async def list(self, common: deps.QueryParams, role: Optional[schemas.Role] = None) -> List[ORMBase]:
        """List resources `model` from database based on `common` query parameters.
        If the current `role` does not conform with combination of `role_name`
        and `permissions[operation]` permissions, `InsufficientPermissions` exception is raised.

        Returns list of specified `schema` instances.
        """
        resources_db = await self.mlist(common, role)
        return [self.schema.from_orm(resource) for resource in resources_db]

    async def mget(self, resource_id: int, role: Optional[schemas.Role] = None) -> BaseModelTortoise:
        """Get single resource from database and do not convert it to pydantic schema"""
        self.check_roles(role, "get")
        try:
            resource_db = await self.model.get(id=resource_id)
            await resource_db.fetch_related(*self.related_fields)
            return resource_db
        except DoesNotExist:
            raise exceptions.ResourceNotFound(self.resource, resource_id)

    async def get(self, resource_id: int, role: Optional[schemas.Role] = None) -> ORMBase:
        """Get single resource from database based on `model`.
        Raises `InsufficientPermissions` exception if role does not conform.
        Raises `ResourceNotFound` exception if the resource is not found by its `resource_id`.

        Returns resource as `response_model`.
        """
        resource_db = await self.mget(resource_id, role)
        return self.schema.from_orm(resource_db)

    async def create(self, resource: schemas.BaseModel, role: Optional[schemas.Role] = None) -> ORMBase:
        """Create resource defined by `resource` schema in the db and return it"""
        self.check_roles(role, "create")
        try:
            resource_db = await self.model.create(**resource.dict(exclude_none=True))
            await resource_db.fetch_related(*self.related_fields)
            return self.schema.from_orm(resource_db)
        except IntegrityError as error:
            logger.error(error)
            raise exceptions.ResourceExistsException(detail=f"{self.resource} already exists in the database")

    async def update(
        self, resource_id: int, resource: schemas.BaseModel, role: Optional[schemas.Role] = None
    ) -> ORMBase:
        """Update resource defined by `resource_id` and schema `resource` in the db and return it"""
        self.check_roles(role, "update")
        try:
            resource_db = await self.model.get(id=resource_id)
            await resource_db.fetch_related(*self.related_fields)
        except DoesNotExist:
            raise exceptions.ResourceNotFound(self.resource, resource_id)
        try:
            await resource_db.update_from_dict(resource.dict(exclude_none=True))
            await resource_db.save()
            await resource_db.fetch_related(*self.related_fields)
            return self.schema.from_orm(resource_db)
        except IntegrityError:
            raise exceptions.ResourceExistsException(detail=f"{self.resource} already exists in the database")

    async def delete(self, resource_id: int, role: Optional[schemas.Role] = None):
        """Delete resource with id `resource_id` from the db."""
        self.check_roles(role, "delete")
        try:
            resource_db = await self.model.get(id=resource_id)
            await resource_db.delete()
        except DoesNotExist:
            raise exceptions.ResourceNotFound(self.resource, resource_id)

    async def add_related(
        self, resource_id: int, related_id: int, related_resource: str, role: Optional[schemas.Role] = None
    ) -> List[ORMBase]:
        """Add {related_id} to attribute {related_resource} of {resource_id}"""
        self.check_roles(role, "update")
        related_definition = self.related_fields[related_resource]
        rmodel, rschema = related_definition.model, related_definition.schema
        try:
            related_db = await rmodel.get(id=related_id)
        except DoesNotExist:
            raise exceptions.ResourceNotFound(str(rmodel), related_id)
        resource_db = await self.mget(resource_id)
        await getattr(resource_db, related_resource).add(related_db)
        await resource_db.fetch_related(related_resource)
        return [rschema.from_orm(nested) for nested in getattr(resource_db, related_resource)]

    async def remove_related(
        self, resource_id: int, related_id: int, related_resource: str, role: Optional[schemas.Role] = None
    ) -> List[ORMBase]:
        """Remove {related_id} from attribute {related_resource} of {resource_id}"""
        self.check_roles(role, "update")
        related_definition = self.related_fields[related_resource]
        rmodel, rschema = related_definition.model, related_definition.schema
        try:
            related_db = await rmodel.get(id=related_id)
        except DoesNotExist:
            raise exceptions.ResourceNotFound(str(rmodel), related_id)
        resource_db = await self.mget(resource_id)
        await getattr(resource_db, related_resource).remove(related_db)
        await resource_db.fetch_related(related_resource)
        return [rschema.from_orm(nested) for nested in getattr(resource_db, related_resource)]
