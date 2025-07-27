from .base import *

import os

APP_ENV = os.environ.get('APP_ENV')

if APP_ENV == 'production':
    from .production import *
else:
    from .development import *
