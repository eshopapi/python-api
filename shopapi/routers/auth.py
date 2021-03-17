"""Login-related API endpoints
"""

import logging

from typing import Optional
from urllib.parse import urljoin
from fastapi import APIRouter, Cookie, Depends

from fastapi_sso.sso.base import SSOBase
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.facebook import FacebookSSO
from fastapi_sso.sso.microsoft import MicrosoftSSO
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from shopapi.schemas import schemas, api
from shopapi.config import Config
from shopapi.helpers import exceptions, dependencies, security
from shopapi import actions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


def _provider_factory(provider: str) -> SSOBase:
    provider_view = router.url_path_for("auth_sso_callback", provider=provider)
    redirect_uri = urljoin(Config.base_url.rstrip("/") + "/", provider_view.lstrip("/"))
    if provider == "facebook":
        if Config.SSO.facebook_enabled and Config.SSO.facebook_client_secret and Config.SSO.facebook_client_id:
            return FacebookSSO(
                client_id=Config.SSO.facebook_client_id,
                client_secret=Config.SSO.facebook_client_secret,
                redirect_uri=redirect_uri,
            )
    elif provider == "google":
        if Config.SSO.google_enabled and Config.SSO.google_client_secret and Config.SSO.google_client_id:
            return GoogleSSO(
                client_id=Config.SSO.google_client_id,
                client_secret=Config.SSO.google_client_secret,
                redirect_uri=redirect_uri,
            )
    elif provider == "microsoft":
        if Config.SSO.microsoft_enabled and Config.SSO.microsoft_client_secret and Config.SSO.microsoft_client_id:
            return MicrosoftSSO(
                client_id=Config.SSO.microsoft_client_id,
                client_secret=Config.SSO.microsoft_client_secret,
                redirect_uri=redirect_uri,
            )
    raise NotImplementedError(f"Provider '{provider}' is not implemented or not allowed")


@router.post("/login")
async def auth_login(user: api.LoginUserIn, permanent: bool = False):
    """Login using username / password"""
    db_user = await actions.user.get_user_by_email(user.email)
    if db_user is None:
        raise exceptions.AuthenticationException()
    if db_user.password is None:
        raise exceptions.AuthenticationException()
    if not security.verify_password(user.password, db_user.password.decode("ascii")):
        raise exceptions.AuthenticationException()
    return await actions.user.login_user(db_user, permanent=permanent)


@router.get("/logout")
async def auth_logout():
    """Logout active user (delete their token from browser's cookies)"""
    response = RedirectResponse(Config.base_url)
    response.delete_cookie("sessiontoken")
    response.delete_cookie("ssostate")
    response.delete_cookie("ssoaction")
    return response


@router.get("/sso/{provider}/login")
async def auth_sso_login(provider: str):
    """Return redirect to sso provider's login"""
    sso = _provider_factory(provider)
    return await sso.get_login_redirect()


@router.get("/sso/{provider}/callback")
async def auth_sso_callback(
    provider: str,
    request: Request,
    redirect_to: Optional[str] = Cookie(None),
    ssoaction: str = Cookie("login"),
    token: Optional[str] = Depends(dependencies.get_user_token),
):
    """Process sso provider's login callback and login user"""
    sso = _provider_factory(provider)
    openidsso = await sso.verify_and_process(request)
    if openidsso is None:
        raise exceptions.AuthenticationException()
    openid = schemas.OpenID.from_sso(openidsso)
    if ssoaction == "add-provider":
        if not token:
            raise exceptions.AuthenticationException()
        logged_user = await dependencies.get_user(token)
        await actions.user.user_add_openid(openid, logged_user.id)
        response = JSONResponse(
            {
                "detail": f"User {logged_user.id} - {logged_user.email} was added "
                f"openid {openid.provider}/{openid.provider_id}"
            }
        )
        response.delete_cookie("ssoaction")
        return response
    user = await actions.user.get_or_create_user(openid)
    return await actions.user.login_user(user, permanent=True, redirect_to=redirect_to, openid=openid)


@router.get("/sso/{provider}/add")
async def auth_sso_add(provider: str, user: schemas.UserToken = Depends(dependencies.get_user)):
    """Begin flow for adding another provider to existing user"""
    logger.info("Requesting to add provider %s for user %d - %s", provider, user.id, user.email)
    sso = _provider_factory(provider)
    response = await sso.get_login_redirect()
    response.set_cookie("ssoaction", "add-provider", expires=300)
    return response
