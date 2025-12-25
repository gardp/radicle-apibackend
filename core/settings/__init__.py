from .base import * 
import os

APP_ENV = os.environ.get('APP_ENV')
if APP_ENV == 'production':
    from .production import *
else:
    from .development import *

# from .celery import app as celery_app
# __all__ = ('celery_app',) # This is for celery to work with django settings