import os
from distutils.util import strtobool as _strtobool

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from . import endpoints
from .auth import JWTAuthBackend
from .database import get_db


def strtobool(val: str, default: bool = False) -> bool:
    try:
        return _strtobool(val)
    except (AttributeError, ValueError):
        return default


MONGODB = os.environ["MONGODB"]
HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])
ALLOW_CORS = strtobool(os.environ.get("ALLOW_CORS"))


async def on_startup():
    endpoints.db = await get_db(MONGODB)
    await endpoints.db.create_index("user", unique=True)


def on_auth_error(request: Request, exc: Exception):
    return PlainTextResponse(str(exc), status_code=401, headers={
        "WWW-Authenticate": "Bearer"
    })


routes = [
    Route("/stats", endpoints.StatisticsEndpoint),
    Route("/vtubers", endpoints.VtubersEndpoint),
    Route("/users", endpoints.UserEndpoint),
    Route("/users/{user}", endpoints.PerUserEndpoint),
    Route("/m2m/subs/{topic}", endpoints.SubsEndpoint),
    Route("/m2m/get_token/{user}", endpoints.JWTEndpoint)
]
middleware = [
    Middleware(AuthenticationMiddleware, backend=JWTAuthBackend(), on_error=on_auth_error)
]
if ALLOW_CORS:
    print("Allow CORS.")
    middleware.insert(0, Middleware(CORSMiddleware, allow_origins=["*"], allow_headers=["*"], allow_methods=["*"]))

app = Starlette(routes=routes, middleware=middleware, on_startup=[on_startup])
uvicorn.run(app, host=HOST, port=PORT, lifespan="on")
