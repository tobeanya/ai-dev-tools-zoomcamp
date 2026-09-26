import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_dev_tools_zoomcamp.settings")

application = get_wsgi_application()
