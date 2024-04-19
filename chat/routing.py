# from django.urls import re_path
from . import consumers

# websocket_urlpatterns = [
#     re_path(r"ws/chat/(?P<receiver_id>\d+)/$", consumers.ChatConsumer.as_asgi()),
# ]

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path, re_path


application = ProtocolTypeRouter(
    {
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        re_path(
                            r"ws/chat/(?P<receiver_id>\d+)/$",
                            consumers.ChatConsumer.as_asgi(),
                        ),
                    ]
                )
            )
        ),
    }
)
