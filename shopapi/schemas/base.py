"""Base for schemas
"""

from typing import List, NamedTuple, Type
from pydantic import BaseModel as PydanticBase  # pylint: disable=no-name-in-module
from tortoise import fields
from tortoise.models import Model


class BaseModelTortoise(Model):
    """BaseModel"""

    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @staticmethod
    def get_search_fields() -> List[str]:
        """List fields that support searching in the current model"""
        return []


class ORMBase(PydanticBase):
    """Base for orm-mode schemas"""

    class Config:
        """Class metadata"""

        orm_mode = True


class ComputedBase(PydanticBase):
    """Base for schemas containing computed properties"""

    @staticmethod
    def get_computed_properties() -> List[str]:
        """Get list of computed properties for the current schema"""
        return []

    def dict(
        self,
        *,
        include=None,
        exclude=None,
        by_alias=False,
        skip_defaults=None,
        exclude_unset=False,
        exclude_defaults=False,
        exclude_none=False
    ):
        """Return as dict"""
        dct = super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        if self.get_computed_properties():
            dct.update(
                {
                    prop: getattr(self, prop)
                    for prop in self.get_computed_properties()
                    if not exclude_none or getattr(self, prop) is not None
                }
            )
        return dct


class ModelDefinition(NamedTuple):
    """NamedTuple to hold model / schema information"""

    model: Type[BaseModelTortoise]
    schema: Type[ORMBase]
