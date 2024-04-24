import os
from django.core.asgi import get_asgi_application
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.consumers import ChatConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myChat.settings')

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(  # Handle websocket connections with authentication
        URLRouter([
            path("ws/chat/<int:receiver_id>/", ChatConsumer.as_asgi()),
        ])
        ),
        # Just HTTP for now. (We can add other protocols later.)
    }
)