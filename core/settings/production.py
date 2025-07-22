# myproject_name/myproject_name/settings/production.py
from .base import *
import os
from django.core.exceptions import ImproperlyConfigured

DEBUG = False # NEVER True in production!

# Allowed hosts (your domain and IP) - MUST be set!
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    raise ImproperlyConfigured("ALLOWED_HOSTS environment variable not set or empty.")

# Database settings for PostgreSQL (will get details from environment variables)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT', 5432), # Default PostgreSQL port
    }
}   

# STATIC FILES (Served by WhiteNoise via Django)
# STATIC_ROOT is where collectstatic will put all static files.
# This will be served by Nginx in production, or Whitenoise if Nginx is configured to pass it.
# We will use Whitenoise for simplicity first.
# The STATIC_ROOT is defined in base.py, collectstatic will populate it.

# MEDIA FILES (User-uploaded, served from DigitalOcean Spaces)
# You'll need django-storages and boto3 for this
INSTALLED_APPS += [
    'storages', # Add this to your INSTALLED_APPS
]

AWS_ACCESS_KEY_ID = os.environ.get('DO_SPACES_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('DO_SPACES_SECRET')
AWS_STORAGE_BUCKET_NAME = os.environ.get('DO_SPACES_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.environ.get('DO_SPACES_ENDPOINT_URL') # e.g., 'https://nyc3.digitaloceanspaces.com'
AWS_S3_CUSTOM_DOMAIN = os.environ.get('DO_SPACES_CUSTOM_DOMAIN') # Optional, if you map a domain to Spaces

# Use S3Boto3Storage for media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/" if AWS_S3_CUSTOM_DOMAIN else f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/media/"
# Adjusting for DigitalOcean Spaces specific settings
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'} # Cache media files for 24 hours
AWS_LOCATION = 'media' # This will be the folder in your bucket for media files

# For static files, we'll use WhiteNoise
# (Ensure 'whitenoise.middleware.WhiteNoiseMiddleware' is in your MIDDLEWARE in base.py)
# STATIC_ROOT is already defined in base.py.
# This will be collected by collectstatic and served by Whitenoise (and potentially Nginx later).
# We use a specific storage class for static files with Whitenoise for compression and caching headers.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# Add WhiteNoise to middleware in base.py, after SecurityMiddleware

# Security settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY' # Or 'SAMEORIGIN' if you embed your site
SECURE_SSL_REDIRECT = True # If Nginx handles SSL, it's already HTTPS
SECURE_HSTS_SECONDS = 31536000 # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email backend (configure for real email service)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Logging (more robust setup for production)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django_info.log', # Create a 'logs' directory
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django_error.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': { # Still useful for systemd output
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'myproject_name': { # Replace with your main Django app name
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Caching (example using Redis, will need to set up Redis later)
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }