# from pathlib import Path
# from decouple import config
# from datetime import timedelta
# import os
# import sys 


# BASE_DIR = Path(__file__).resolve().parent.parent

# # Decouple will automatically find and load the .env file.
# SECRET_KEY = config('DJANGO_SECRET_KEY')
# DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

# ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='127.0.0.1').split(',')

# # Media files (user-uploaded files)
# MEDIA_URL = '/media/'
# # This is the absolute path to the directory where uploaded files will be stored.
# # Create a 'media' folder in your project root or an app's root.
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# INSTALLED_APPS = [
#     # Third party apps
#     'rest_framework',
#     'corsheaders',
#     'rest_framework_simplejwt',
#     # Django apps
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     # Local apps
#     'api.apps.ApiConfig',
#     'custom_users.apps.CustomUsersConfig',
#     'music.apps.MusicConfig',
#     'payments.apps.PaymentsConfig',
#     'licenses.apps.LicensesConfig',
# ]

# MIDDLEWARE = [
#     'corsheaders.middleware.CorsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'core.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = 'core.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]

# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'
# USE_I18N = True
# USE_TZ = True

# STATIC_URL = 'static/'

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000", # React dev server
# ]

# # If you need to allow specific headers or methods beyond defaults
# CORS_ALLOW_METHODS = [
#     'DELETE',
#     'GET',
#     'OPTIONS',
#     'PATCH',
#     'POST',
#     'PUT',
# ]

# CORS_ALLOW_HEADERS = [
#     'accept',
#     'accept-encoding',
#     'authorization',
#     'content-type',
#     'dnt',
#     'origin',
#     'user-agent',
#     'x-csrftoken',
#     'x-requested-with',
# ]

# # If you need to allow credentials (e.g., cookies, although JWT usually doesn't need them directly for access token)
# CORS_ALLOW_CREDENTIALS = True

# REST_FRAMEWORK = {
#     'DEFAULT_PERMISSION_CLASSES': [
#         # 'rest_framework.permissions.IsAuthenticated',
#         'rest_framework.permissions.AllowAny', # For public endpoints...so maybe i'll have to change to isauthenticated for payments and licenses endpoints
#     ],
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.SessionAuthentication',
#         'rest_framework.authentication.BasicAuthentication',
#         # 'rest_framework_simplejwt.authentication.JWTAuthentication',
#     ],
#     'DEFAULT_RENDERER_CLASSES': [
#         'rest_framework.renderers.JSONRenderer',
#         'rest_framework.renderers.BrowsableAPIRenderer', # For convenient browser testing
#     ],
# }

# SIMPLE_JWT = {
#     "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5), # Short-lived for security
#     "REFRESH_TOKEN_LIFETIME": timedelta(days=7),   # Longer-lived for convenience
#     "ROTATE_REFRESH_TOKENS": False, # Set to True for enhanced security if you rotate
#     "BLACKLIST_AFTER_ROTATION": False, # Set to True if rotating refresh tokens
#     "UPDATE_LAST_LOGIN": True,

#     "ALGORITHM": "HS256",
#     "SIGNING_KEY": SECRET_KEY, # Uses your Django SECRET_KEY for signing
#     "VERIFYING_KEY": None,
#     "AUDIENCE": None,
#     "ISSUER": None,
#     "JWK_URL": None,
#     "LEEWAY": 0,

#     "AUTH_HEADER_TYPES": ("Bearer",), # The token type in the Authorization header
#     "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
#     "USER_ID_FIELD": "id",
#     "USER_ID_CLAIM": "user_id",
#     "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

#     "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
#     "TOKEN_TYPE_CLAIM": "token_type",
#     "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

#     "JTI_CLAIM": "jti",

#     "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
#     "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
#     "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

#     "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
#     "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
#     "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
#     "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
#     "TOKEN_SLIDING_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
#     "TOKEN_SLIDING_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
# }

# if 'test' in sys.argv:
#     print("========== DATABASE CONNECTION SETTINGS ==========")
#     print(f"DB_NAME: {config('DB_NAME')}")
#     print(f"DB_USER: {config('DB_USER')}")
#     print(f"DB_HOST: {config('DB_HOST')}")
#     print(f"DB_PORT: {config('DB_PORT')}")
#     # Don't print the actual password for security
#     print("DB_PASSWORD: [hidden]")
#     print("==================================================")

# # You can optionally add this to settings.py to customize test database name
# TEST = {
#     'NAME': 'test_radicle_db',
# }