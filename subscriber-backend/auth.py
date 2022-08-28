import os

import jwt
from starlette.authentication import (AuthCredentials, AuthenticationBackend, AuthenticationError, SimpleUser)

M2M_TOKEN = os.environ["M2M_TOKEN"]
SECRET_TOKEN = os.environ["SECRET_TOKEN"]


class JWTAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        if "Authorization" not in request.headers:
            return

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
        except ValueError:
            return

        if scheme.lower() != 'bearer':
            return

        if credentials == M2M_TOKEN:
            return AuthCredentials(["authenticated", "admin"]), SimpleUser("admin")
        else:
            try:
                decoded = jwt.decode(credentials, SECRET_TOKEN, algorithms=["HS256"])
            except jwt.InvalidTokenError:
                print(credentials)
                raise AuthenticationError('Invalid auth credentials')

            return AuthCredentials(["authenticated", "user"]), SimpleUser(decoded["user"])
