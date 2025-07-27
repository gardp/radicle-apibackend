# myproject_name/myproject_name/settings/development.py
from .base import *
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# Now you can access them via os.environ.get, or rely on base.py's
# os.environ.get calls to pick them up after load_dotenv()
# For example, in base.py:
# SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
# DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
DEBUG = True # Enable debug for development
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# SQLite database for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# For static/media serving during development (Django's dev server)
# No need for STATIC_ROOT/MEDIA_ROOT specific overrides here for simple dev,
# Django's dev server handles it from app static folders + STATICFILES_DIRS
# Add your app's 'static' directories if you haven't already in base.py
# For development, you might need STATICFILES_DIRS if you have project-level static files:
# STATICFILES_DIRS = [
#     BASE_DIR / 'static_dev', # Example for project-level static files in dev
# ]

# Console email backend for dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Optional: Django Debug Toolbar settings if you use it
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
# INTERNAL_IPS = ['127.0.0.1']