"""Database models for Tortoise-ORM operations
"""

from tortoise import Tortoise, fields, run_async
from tortoise.models import Model

TORTOISE_ORM = {
    "connections": {"default": "sqlite://db.sqlite3"},
    "apps": {
        "models": {
            "models": ["shopapi.schemas.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


class BaseModel(Model):
    """BaseModel"""

    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted = fields.BooleanField(default=False)


class User(BaseModel):
    """User"""

    email = fields.CharField(unique=True, max_length=256)
    password = fields.BinaryField(null=True)
    first_name = fields.CharField(max_length=64, null=True)
    last_name = fields.CharField(max_length=64, null=True)
    picture = fields.CharField(max_length=1024, null=True)


class OpenID(BaseModel):
    """OpenID"""

    user = fields.ForeignKeyField("models.User", related_name="openids", null=True)
    email = fields.CharField(max_length=256)
    first_name = fields.CharField(max_length=64, null=True)
    last_name = fields.CharField(max_length=64, null=True)
    display_name = fields.CharField(max_length=128, null=True)
    picture = fields.CharField(max_length=1024, null=True)
    provider = fields.CharField(max_length=32)
    provider_id = fields.CharField(max_length=64)
