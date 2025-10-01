import os
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Set default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth.settings")

application = get_wsgi_application()
