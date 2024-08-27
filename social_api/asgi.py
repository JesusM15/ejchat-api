import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_api.settings')

django_application = get_asgi_application()

from social_api.routing import websocket_urlpatterns
from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": django_application,
    "websocket": AllowedHostsOriginValidator
        (AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
                + chat_websocket_urlpatterns
            )
        )
    ),
})
