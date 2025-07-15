# custom_users/views.py

from rest_framework import generics, permissions
from rest_framework.response import Response # For custom responses, if needed
from rest_framework.views import APIView     # For custom API views, if generics aren't enough

from django.contrib.auth import get_user_model # Get your custom user model
from .serializers import UserSerializer, UserProfileSerializer # Import your serializers
from .models import UserProfile # Only if you need to query UserProfile directly in a view

# Get the active User model (which will be your CustomUser)
User = get_user_model()

# custom_users/views.py (Continuing from imports)

class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny] # Anyone can register

    # Optional: You might want to automatically log in the user after registration
    # Or return tokens if using JWT. This requires more logic, not included for simplicity.

# custom_users/views.py (Continuing)

class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser] # Only admin users can see the full list

# custom_users/views.py (Continuing)

class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk' # The URL will use 'pk' (primary key) to identify the user

    # Permissions:
    # IsAuthenticated means only logged-in users can access this.
    # You might want a custom permission class to ensure users can only
    # view/edit their *own* profile, or that admins can view/edit any.
    permission_classes = [permissions.IsAuthenticated]

    # Custom method to allow 'me' as a lookup for the current user
    def get_object(self):
        obj = super().get_object() # Try to get the object by PK first
        # If the lookup_field was 'me' and the user is authenticated,
        # return the request.user object
        if self.kwargs['pk'] == 'me' and self.request.user.is_authenticated:
            return self.request.user
        return obj # Otherwise, return the object found by PK

# custom_users/views.py (Continuing)

class UserProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all() # Queryset for UserProfile
    serializer_class = UserProfileSerializer # Serializer for UserProfile
    permission_classes = [permissions.IsAuthenticated]

    # This ensures users can only access their *own* profile
    def get_object(self):
        # We access the profile related to the currently authenticated user
        return self.request.user.profile

