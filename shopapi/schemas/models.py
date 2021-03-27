"""Database models for Tortoise-ORM operations
"""

from typing import List, Optional
from tortoise import fields
from shopapi.schemas.base import BaseModelTortoise

from shopapi.config import build_db_url

TORTOISE_ORM = {
    "connections": {"default": build_db_url()},
    "apps": {
        "models": {
            "models": ["shopapi.schemas.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


def strbool(val: bool) -> str:
    """Return boolean as a string"""
    return "true" if val else "false"


def boolstr(val: str) -> bool:
    """Return string as a boolean"""
    return val.lower() in ("yes", "true", "1")


class Shop(BaseModelTortoise):
    """Shop"""

    key = fields.CharField(unique=True, max_length=32, index=True)
    value = fields.CharField(max_length=1024, null=True)  # type: str

    @staticmethod
    def get_search_fields() -> List[str]:
        return ["key", "value"]

    @classmethod
    async def get_bool(cls, key: str) -> bool:
        """Returns flag from the database by its key"""
        dbmod = await cls.get_settings(key)
        if dbmod is None or dbmod.value is None:
            return False
        return boolstr(dbmod.value)

    @classmethod
    async def set_bool(cls, key: str, val: bool = True):
        """Set flag in the database by its key"""
        dbmod = await cls.get_settings(key)
        if dbmod is None:
            await cls.create(key=key, value=strbool(val))
        else:
            dbmod.value = strbool(val)
            await dbmod.save()

    @classmethod
    async def get_settings(cls, key: str) -> Optional["Shop"]:
        """Get settings by key"""
        dbmod = await cls.filter(key=key).first()
        if not dbmod:
            return None
        return dbmod

    @classmethod
    async def is_initialized(cls) -> bool:
        """Returns True if the Shop has already been initialized"""
        return await cls.get_bool("initialized")

    @classmethod
    async def set_initialized(cls, val: bool = True):
        """Set initialized flag"""
        await cls.set_bool("initialized", val)

    @classmethod
    async def is_production(cls) -> bool:
        """Returns True if the Shop is in production mode"""
        return await cls.get_bool("production")

    @classmethod
    async def set_production(cls, val: bool = True):
        """Set production flag"""
        await cls.set_bool("production", val)


class Role(BaseModelTortoise):
    """Role"""

    title = fields.CharField(unique=True, max_length=64)
    roles = fields.IntField()
    assigned_users: fields.ReverseRelation["User"]
    users = fields.IntField()
    tags = fields.IntField(default=0)
    categories = fields.IntField(default=0)
    products = fields.IntField(default=0)

    @staticmethod
    def get_search_fields() -> List[str]:
        return ["title"]


class User(BaseModelTortoise):
    """User"""

    email = fields.CharField(unique=True, max_length=256)
    password_hash = fields.BinaryField(null=True)
    first_name = fields.CharField(max_length=64, null=True)
    last_name = fields.CharField(max_length=64, null=True)
    picture = fields.CharField(max_length=1024, null=True)
    role: fields.ForeignKeyRelation[Role] = fields.ForeignKeyField(
        "models.Role", related_name="assigned_users"
    )  # type: ignore

    @staticmethod
    def get_search_fields() -> List[str]:
        return ["email", "first_name", "last_name"]


class OpenID(BaseModelTortoise):
    """OpenID"""

    user = fields.ForeignKeyField("models.User", null=True)
    email = fields.CharField(max_length=256)
    first_name = fields.CharField(max_length=64, null=True)
    last_name = fields.CharField(max_length=64, null=True)
    display_name = fields.CharField(max_length=128, null=True)
    picture = fields.CharField(max_length=1024, null=True)
    provider = fields.CharField(max_length=32)
    provider_id = fields.CharField(max_length=64)


class Tag(BaseModelTortoise):
    """Tag"""

    name = fields.CharField(max_length=256, unique=True)
    categories: fields.ReverseRelation["Category"]

    @staticmethod
    def get_search_fields() -> List[str]:
        return ["name"]


class Category(BaseModelTortoise):
    """Category"""

    title = fields.CharField(max_length=256, index=True, unique=True)
    parent_category: fields.ForeignKeyNullableRelation["Category"] = fields.ForeignKeyField(
        "models.Category", related_name="child_categories", null=True
    )  # type: ignore
    child_categories = fields.ReverseRelation["Category"]
    tags: fields.ManyToManyRelation["Tag"] = fields.ManyToManyField(
        "models.Tag", through="category_tag", related_name="categories"
    )

    @staticmethod
    def get_search_fields() -> List[str]:
        return ["title"]


# TODO: stub
class Product(BaseModelTortoise):
    """Product"""

    title = fields.CharField(max_length=256, index=True)
    category: fields.ForeignKeyNullableRelation["Category"] = fields.ForeignKeyField(
        "models.Category", null=True
    )  # type:ignore
    tags: fields.ManyToManyRelation["Tag"] = fields.ManyToManyField("models.Tag", through="product_tag")
    short_description = fields.CharField(max_length=1024, index=True)
