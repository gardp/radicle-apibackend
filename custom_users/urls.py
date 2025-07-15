# custom_users/urls.py

from django.urls import path

# Import your views from the local views.py file
# Adjust these imports based on the actual names of your views in custom_users/views.py
from .views import (
    UserRegisterAPIView,
    UserListAPIView,        # For listing all users (often admin-only)
    UserDetailAPIView,      # For retrieving/updating/deleting individual users
    UserProfileRetrieveUpdateAPIView, # If you have a separate profile view
)

# Optional: For JWT (JSON Web Token) authentication
# Make sure you have installed it: pip install djangorestframework-simplejwt
from rest_framework_simplejwt.views import (
    TokenObtainPairView,    # For getting access and refresh tokens
    TokenRefreshView,       # For refreshing an expired access token
)

# custom_users/urls.py (Continuing from Step 2)

urlpatterns = [
    # --- User Management Endpoints ---

    # 1. User Registration:
    # URL: /api/v1/accounts/register/ (assuming your project's urls.py prefixes it)
    # Method: POST
    # Purpose: To create a new user account.
    path('register/', UserRegisterAPIView.as_view(), name='user-register'),

    # 2. User List (typically admin/staff only for security reasons):
    # URL: /api/v1/accounts/users/
    # Method: GET
    # Purpose: To retrieve a list of all user accounts.
    path('users/', UserListAPIView.as_view(), name='user-list'),

    # 3. User Detail (Retrieve, Update, Delete for a specific user by ID):
    # URL: /api/v1/accounts/users/<int:pk>/ (e.g., /api/v1/accounts/users/1/)
    # Method: GET, PUT, PATCH, DELETE
    # Purpose: To get, update, or delete a specific user by their primary key (ID).
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),

    # 4. User Profile (Accessing the current authenticated user's profile):
    # URL: /api/v1/accounts/profile/
    # Method: GET, PUT, PATCH
    # Purpose: To retrieve or update the profile details of the currently authenticated user.
    path('profile/', UserProfileRetrieveUpdateAPIView.as_view(), name='user-profile'),

    # --- Authentication Endpoints (Using Simple JWT as an example) ---

    # 5. Token Obtain (Login):
    # URL: /api/v1/accounts/token/
    # Method: POST (send username and password)
    # Purpose: To get a new access token and refresh token upon successful login.
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # 6. Token Refresh:
    # URL: /api/v1/accounts/token/refresh/
    # Method: POST (send refresh token)
    # Purpose: To get a new access token when the current one expires, using the refresh token.
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- You can add more paths here as your API grows ---
    # For example: password reset, email verification, etc.
]