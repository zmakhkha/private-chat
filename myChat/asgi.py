import os
from django.core.asgi import get_asgi_application
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.consumers import ChatConsumer
import userman.middleware as md


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myChat.settings')

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
        # "websocket": md.JwtMiddleware(
        URLRouter([
            path("ws/chat/<int:receiver_id>/", ChatConsumer.as_asgi()),
        ])
        ),
    }
)