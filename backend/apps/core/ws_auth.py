from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from jwt import decode as jwt_decode
from django.conf import settings


@database_sync_to_async
def get_user(user_id):
    User = get_user_model()
    try:
        return User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get("query_string", b"").decode())
        token = (query.get("token") or [None])[0]
        headers = dict(scope.get("headers") or [])
        org_id = headers.get(b"x-organization-id", b"").decode() or (query.get("organization_id") or [None])[0]
        scope["organization_id"] = org_id
        if not token:
            scope["user"] = AnonymousUser()
            return await super().__call__(scope, receive, send)
        try:
            UntypedToken(token)
            decoded = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            scope["user"] = await get_user(decoded.get("user_id"))
        except (InvalidToken, TokenError, Exception):
            scope["user"] = AnonymousUser()
        return await super().__call__(scope, receive, send)


