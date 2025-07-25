from rest_framework import serializers
from .models import Track

# Serializer for Track
class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = '__all__'
