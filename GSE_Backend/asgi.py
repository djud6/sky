"""
ASGI config for GSE_Backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GSE_Backend.settings')
os.environ.setdefault('SERVER_GATEWAY_INTERFACE', 'ASGI')

application = get_asgi_application()
