"""
WSGI config for GSE_Backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GSE_Backend.settings')
os.environ.setdefault('SERVER_GATEWAY_INTERFACE', 'WSGI')

application = get_wsgi_application()
