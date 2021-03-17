"""Main module for running shopapi server
"""

import os
from fastapi import FastAPI
from dotenv import load_dotenv

from tortoise.contrib.fastapi import register_tortoise

from shopapi import routers
from shopapi.config import build_db_url

_basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(_basedir, ".env"))

app = FastAPI(
    redoc_url=None, title="ShopAPI", description="Made possible with `FastAPI`, `tortoise-orm` and many others"
)


@app.get("/")
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
