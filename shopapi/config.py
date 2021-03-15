"""Configuration proxy
"""

import os
from base64 import b64encode

from typing import Any, List, Optional, Type
import config_proxy


class ConfigProxy(config_proxy.ConfigProxy):
    """ConfigProxy"""

    env_location: str = "SHOPAPI_CONFIG"
    config_file_names: List[str] = ["config.json", "shopapi.json"]


class StringProperty(config_proxy.StringProperty):
    """StringProperty"""

    def __init__(
        self,
        path: Optional[str] = None,
        env: Optional[str] = None,
        default: Optional[Any] = None,
        proxy: Type[config_proxy.ConfigProxy] = ConfigProxy,
    ):
        super().__init__(path=path, env=env, default=default, proxy=proxy)


class IntProperty(config_proxy.IntProperty):
    """IntProperty"""

    def __init__(
        self,
        path: Optional[str] = None,
        env: Optional[str] = None,
        default: Optional[Any] = None,
        proxy: Type[config_proxy.ConfigProxy] = ConfigProxy,
    ):
        super().__init__(path=path, env=env, default=default, proxy=proxy)


class BoolProperty(config_proxy.ConfigProperty):
    """BoolProperty"""

    def __init__(
        self,
        path: Optional[str],
        env: Optional[str],
        default: Optional[Any],
        proxy: Type[config_proxy.ConfigProxy] = ConfigProxy,
    ):
        super().__init__(path=path, env=env, default=default, proxy=proxy)

    @property
    def value(self) -> bool:
        return super().get_value(use_list=False)


class Config:
    """Main Configuration Proxy to access settings either via json configuration,
    an environmental variable or specified default
    """

    secret_key = StringProperty("secret_key", "SHOPAPI__SECRET_KEY", b64encode(os.urandom(128)).decode("ascii")).fvalue
    access_token_expire = IntProperty("access_token_expire", "SHOPAPI__ACCESS_TOKEN_EXPIRE", 60).fvalue
    base_url = StringProperty("base_url", "SHOPAPI__BASE_URL", "http://localhost").fvalue
    support_contact = StringProperty("support_contact", "SHOPAPI__SUPPORT_CONTACT").value

    class Database:
        """Database settings"""

        host = StringProperty("database.host", "SHOPAPI__DB_HOST", "db.sqlite3").value
        port = IntProperty("database.port", "SHOPAPI__DB_PORT").value
        backend = StringProperty("database.backend", "SHOPAPI__DB_BACKEND", "sqlite").value
        user = StringProperty("database.user", "SHOPAPI__DB_USER").value
        password = StringProperty("database.password", "SHOPAPI__DB_PASS").value
        database = StringProperty("database.database", "SHOPAPI__DB_NAME", "shopapi").fvalue

    class SSO:
        """SSO Settings"""

        google_enabled = BoolProperty("sso.google.enabled", "SHOPAPI__SSO_GOOGLE_ENABLED", False).fvalue
        google_client_id = StringProperty("sso.google.client_id", "SHOPAPI__SSO_GOOGLE_CLIENT_ID").value
        google_client_secret = StringProperty("sso.google.client_secret", "SHOPAPI__SSO_GOOGLE_CLIENT_SECRET").value
        facebook_enabled = BoolProperty("sso.facebook.enabled", "SHOPAPI__SSO_FACEBOOK_ENABLED", False).fvalue
        facebook_client_id = StringProperty("sso.facebook.client_id", "SHOPAPI__SSO_FACEBOOK_CLIENT_ID").value
        facebook_client_secret = StringProperty(
            "sso.facebook.client_secret", "SHOPAPI__SSO_FACEBOOK_CLIENT_SECRET"
        ).value
        microsoft_enabled = BoolProperty("sso.microsoft.enabled", "SHOPAPI__SSO_MICROSOFT_ENABLED", False).fvalue
        microsoft_client_id = StringProperty("sso.microsoft.client_id", "SHOPAPI__SSO_MICROSOFT_CLIENT_ID").value
        microsoft_client_secret = StringProperty(
            "sso.microsoft.client_secret", "SHOPAPI__SSO_MICROSOFT_CLIENT_SECRET"
        ).value


def build_db_url() -> str:
    """Build DB tortoise orm url for connection from Config object"""
    if Config.Database.backend == "sqlite":
        return f"sqlite://{Config.Database.host}"
    if Config.Database.backend == "postgres":
        return (
            f"postgres://{Config.Database.user}:{Config.Database.password}"
            f"@{Config.Database.host}/{Config.Database.database}"
        )
    raise NotImplementedError(f"DB Backend {Config.Database.backend} is not implemented")
