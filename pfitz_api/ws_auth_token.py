from channels.db import database_sync_to_async
from knox.auth import TokenAuthentication
from django.contrib.auth import get_user_model
from rest_framework import HTTP_HEADER_ENCODING

import logging

logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user(token):
    knoxAuth = TokenAuthentication()
    user, auth_token = knoxAuth.authenticate_credentials(token.encode(HTTP_HEADER_ENCODING))
    return user

class CustomAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).
        logger.debug("CustomAuthMiddleware call func. scope['query_string'] = %s", scope["query_string"].decode())

        scope['user'] = await get_user(scope["query_string"].decode().split("=")[1])

        return await self.app(scope, receive, send)
