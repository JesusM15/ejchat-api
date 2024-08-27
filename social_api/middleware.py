from channels.middleware.base import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
import json

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Obtener el token del encabezado de la solicitud WebSocket
        headers = dict(scope['headers'])
        auth_header = headers.get(b'authorization')
        token = None

        if auth_header:
            token = auth_header.decode().split(' ')[1]

        # Verificar el token
        if token:
            try:
                # Verificar el token
                user, _ = JWTAuthentication().authenticate_credentials(token)
                scope['user'] = user
            except Exception as e:
                # Manejar token inválido o errores
                scope['user'] = AnonymousUser()
                print(f"JWT Authentication Error: {e}")
        else:
            scope['user'] = AnonymousUser()

        # Llamar al siguiente middleware
        await super().__call__(scope, receive, send)
