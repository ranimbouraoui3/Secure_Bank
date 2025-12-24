"""
WSGI config for banking_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""
import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command
from django.db import ProgrammingError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_project.settings')

# Try to create the cache table if it doesn't exist
try:
    # Remove 'interactive=False', it's not a valid argument
    call_command('createcachetable')
except ProgrammingError:
    # Table already exists, ignore
    pass

application = get_wsgi_application()