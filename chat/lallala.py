from django.urls import path
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from myapp.consumers import ChatConsumer  # Import your WebSocket consumer class

# Django ASGI application
django_asgi_app = get_asgi_application()

# Websocket protocol router
application = ProtocolTypeRouter({
    "http": django_asgi_app,  # Handle HTTP connections with Django
    "websocket": AuthMiddlewareStack(  # Handle websocket connections with authentication
        URLRouter([
            path("ws/chat/<int:receiver_id>/", ChatConsumer.as_asgi()),
        ])
    ),
})
