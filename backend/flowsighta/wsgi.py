import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowsighta.settings_dev")

application = get_wsgi_application

