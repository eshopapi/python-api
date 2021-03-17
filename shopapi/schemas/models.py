"""Database models for Tortoise-ORM operations
"""

from typing import Optional
from tortoise import fields
from tortoise.models import Model

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
    return val.lower() in ["yes", "true", "1"]


class BaseModel(Model):
    """BaseModel"""

    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted = fields.BooleanField(default=False)


class Shop(BaseModel):
    """Shop"""

    key = fields.CharField(unique=True, max_length=32, index=True)
    value = fields.CharField(max_length=1024, null=True)  # type: str

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
        dbmod = await cls.get_settings("initialized")
        if dbmod is None or dbmod.value is None:
            return False
        return boolstr(dbmod.value)

    @classmethod
    async def set_initialized(cls, val: bool = True):
        """Set initialized flag"""
        dbmod = await cls.get_settings("initialized")
        if dbmod is None:
            await cls.create(key="initialized", value=strbool(val))
        else:
            dbmod.value = strbool(val)
            await dbmod.save()


class Role(BaseModel):
    """Role"""

    title = fields.CharField(unique=True, max_length=64)
    roles = fields.IntField()
    assigned_users: fields.ReverseRelation["User"]
    users = fields.IntField()


class User(BaseModel):
    """User"""

    email = fields.CharField(unique=True, max_length=256)
    password = fields.BinaryField(null=True)
    first_name = fields.CharField(max_length=64, null=True)
    last_name = fields.CharField(max_length=64, null=True)
    picture = fields.CharField(max_length=1024, null=True)
    role: fields.ForeignKeyRelation[Role] = fields.ForeignKeyField(
        "models.Role", related_name="assigned_users"
    )  # type: ignore


class OpenID(BaseModel):
    """OpenID"""

    user = fields.ForeignKeyField("models.User", null=True)
    email = fields.CharField(max_length=256)
    first_name = fields.CharField(max_length=64, null=True)
    last_name = fields.CharField(max_length=64, null=True)
    display_name = fields.CharField(max_length=128, null=True)
    picture = fields.CharField(max_length=1024, null=True)
    provider = fields.CharField(max_length=32)
    provider_id = fields.CharField(max_length=64)
