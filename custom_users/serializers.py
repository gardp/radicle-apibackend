# custom_users/serializers.py (Example structure)
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile # Import UserProfile if you have it

User = get_user_model() # Get your CustomUser model

# Serializer for UserProfile (if you have one)
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'bio', 'location', 'avatar']
        read_only_fields = ['user'] # 'user' is often managed by the view or signals

# Serializer for CustomUser
class UserSerializer(serializers.ModelSerializer):
    # Nested serializer for the user's profile.
    # 'read_only=True' means this field is included in GET responses,
    # but not expected in POST/PUT requests for creating/updating the user directly.
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        # Fields to include in API responses and/or allow for creation/update
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'profile']
        # extra_kwargs is crucial for handling sensitive fields like password
        extra_kwargs = {
            'password': {'write_only': True} # Password can be written (for creation/update) but not read (retrieved)
        }

    # Override create to correctly handle password hashing for new users
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password is not None:
            user.set_password(password) # Hash the password!
            user.save()
        return user

    # Override update to correctly handle password hashing for updates
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password is not None:
            user.set_password(password)
            user.save()
        return user