import os
import time
from json import JSONDecodeError
from typing import Optional
from urllib.parse import urljoin

import jwt
from httpx import AsyncClient
from httpx import HTTPError
from motor.core import AgnosticCollection
from starlette.authentication import requires
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.responses import PlainTextResponse
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, \
    HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR

from .schema import default_dict, validate

SECRET_TOKEN = os.environ["SECRET_TOKEN"]
UPSTREAM_URL = os.environ["UPSTREAM_URL"]
http = AsyncClient()
db: Optional[AgnosticCollection] = None


class PerUserEndpoint(HTTPEndpoint):
    @requires("authenticated", status_code=HTTP_401_UNAUTHORIZED)
    async def get(self, request: Request):
        user = request.path_params["user"]
        token_user = request.user.display_name
        if not (token_user in [user, "admin"]):
            return PlainTextResponse("Forbidden", status_code=HTTP_403_FORBIDDEN)

        if not (user_entry := await db.find_one({"user": user})):
            return PlainTextResponse("Not Found", status_code=HTTP_404_NOT_FOUND)

        user_entry.pop("user")
        user_entry.pop("_id")

        if not validate(user_entry)[0]:
            return PlainTextResponse("Wrong entry schema in db.", status_code=HTTP_500_INTERNAL_SERVER_ERROR)
        return JSONResponse(user_entry)

    @requires("authenticated", status_code=HTTP_401_UNAUTHORIZED)
    async def put(self, request: Request):
        user = request.path_params["user"]
        token_user = request.user.display_name
        if not (token_user in [user, "admin"]):
            return PlainTextResponse("Forbidden", status_code=HTTP_403_FORBIDDEN)

        try:
            payload = await request.json()
        except JSONDecodeError:
            return Response(status_code=HTTP_400_BAD_REQUEST)
        schema_pass, schema_error_msg = validate(payload)
        if not schema_pass:
            return PlainTextResponse(schema_error_msg, status_code=HTTP_400_BAD_REQUEST)

        payload["user"] = user
        result = await db.update_one({"user": user}, {"$set": payload})

        if result.matched_count == 0:
            return PlainTextResponse("Not Found", status_code=HTTP_404_NOT_FOUND)

        return Response(status_code=HTTP_204_NO_CONTENT)

    @requires("authenticated", status_code=HTTP_401_UNAUTHORIZED)
    async def delete(self, request: Request):
        user = request.path_params["user"]
        token_user = request.user.display_name
        if not (token_user in [user, "admin"]):
            return PlainTextResponse("Forbidden", status_code=HTTP_403_FORBIDDEN)

        result = await db.delete_one({"user": user})
        if result.deleted_count == 0:
            return PlainTextResponse("Not Found", status_code=HTTP_404_NOT_FOUND)
        return Response(status_code=HTTP_204_NO_CONTENT)


class UserEndpoint(HTTPEndpoint):
    @requires("admin", status_code=HTTP_401_UNAUTHORIZED)
    async def get(self, request: Request):
        all_users = []
        async for user in db.find():
            all_users.append(user["user"])
        return JSONResponse(all_users)

    @requires("admin", status_code=HTTP_401_UNAUTHORIZED)
    async def post(self, request: Request):
        user = (await request.body()).decode("utf-8")
        if await db.find_one({"user": user}):
            return PlainTextResponse("Conflict", status_code=HTTP_409_CONFLICT)

        await db.insert_one({"user": user, **default_dict})
        return Response(status_code=HTTP_204_NO_CONTENT)


class JWTEndpoint(HTTPEndpoint):
    @requires("admin", status_code=HTTP_401_UNAUTHORIZED)
    async def get(self, request: Request):
        user = request.path_params["user"]
        if not await db.find_one({"user": user}):
            return PlainTextResponse("Not Found", status_code=HTTP_404_NOT_FOUND)

        expire = request.path_params.get("exp", 600)
        now = int(time.time())
        token = jwt.encode({"user": user, "exp": now + expire}, SECRET_TOKEN, algorithm="HS256")
        return PlainTextResponse(token)


class SubsEndpoint(HTTPEndpoint):
    @requires("admin", status_code=HTTP_401_UNAUTHORIZED)
    async def get(self, request: Request):
        topic = request.path_params["topic"]
        event_type = request.query_params.get("type")

        query = {"sub": {"$all": [topic]}}
        if event_type:
            query["notif"] = {"$all": [event_type]}
        users = []
        async for user in db.find(query):
            users.append(user["user"])

        return JSONResponse(users)


class VtubersEndpoint(HTTPEndpoint):
    async def get(self, request: Request):
        try:
            resp = await http.get(urljoin(UPSTREAM_URL, "api/vtubers"))
        except HTTPError:
            return PlainTextResponse("Internal Server Error", status_code=HTTP_500_INTERNAL_SERVER_ERROR)

        return JSONResponse(resp.json())


class StatisticsEndpoint(HTTPEndpoint):
    async def get(self, request: Request):
        try:
            resp = await http.get(urljoin(UPSTREAM_URL, "api/vtubers"))
            vtubers_count = len(resp.json())
        except (HTTPError, JSONDecodeError):
            return PlainTextResponse("Internal Server Error", status_code=HTTP_500_INTERNAL_SERVER_ERROR)

        subscribers_count = await db.estimated_document_count()

        data = {"vtubers": vtubers_count, "subscribers": subscribers_count}
        return JSONResponse(data)
