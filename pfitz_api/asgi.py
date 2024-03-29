"""
ASGI config for pfitz_api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pfitz_api.settings')

from django.core.asgi import get_asgi_application
asgi_app = get_asgi_application()
from .ws_auth_token import CustomAuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from zimgpt.routing import urlpatterns

application = ProtocolTypeRouter({
    "http": asgi_app,
    "websocket": CustomAuthMiddleware(
            URLRouter(urlpatterns)
        )
})
