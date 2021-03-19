"""Main module for running shopapi server
"""

import os
import logging
from fastapi import FastAPI
from dotenv import load_dotenv

from tortoise.contrib.fastapi import register_tortoise

from shopapi import routers
from shopapi.config import build_db_url

# TODO: Logging from config to keep everything in one place?
logging.basicConfig(format="[%(asctime)s] <%(name)s> %(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

_basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(_basedir, ".env"))

tags = [
    {"name": "General", "description": "Generic endpoints that belong nowhere else."},
    {"name": "Authentication", "description": "Authenticate user, create openid and manage openid associations."},
    {"name": "Users", "description": "Endpoints used to manage users and role associations."},
    {"name": "Service", "description": "Service endpoint used to manager ShopAPI environment and deployment."},
]

app = FastAPI(
    redoc_url=None,
    title="ShopAPI",
    description="Made possible with `FastAPI`, `tortoise-orm` and many others",
    openapi_tags=tags,
)


@app.get("/", tags=["General"], name="The Room Easter Egg")
def index():
    """> I did not hit her, I did not.
    >
    > -- <cite>Tommy</cite>
    """
    return {"message": "Oh, hi, Mark!"}


app.include_router(routers.auth.router)
app.include_router(routers.user.router)
app.include_router(routers.service.router)

register_tortoise(app, db_url=build_db_url(), modules={"models": ["shopapi.schemas.models"]}, generate_schemas=True)
