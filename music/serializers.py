from rest_framework import serializers
from .models import Track, Publisher, Contributor, Publishing, Contribution, Library, SocialMediaLink, MusicProfessional, FileFormat, TrackStorageFile
# from licenses.serializers import LicenseTypeSerializer

# Serializer for Track
class TrackSerializer(serializers.ModelSerializer):
    # Nested serializers for related objects to access in the track api endpoint
    class Meta:
        model = Track
        fields = '__all__'
    
    
    # def get_contributions(self, obj):
    #     from .serializers import ContributionSerializer  # Import here to avoid circular imports
    #     contributions = obj.contributions.all()
    #     return ContributionSerializer(contributions, many=True).data
    
    # def get_libraries(self, obj):
    #     from .serializers import LibrarySerializer  # Import here to avoid circular imports
    #     # Make sure the related_name in your model is 'libraries', otherwise use the correct one
    #     libraries = obj.libraries.all() if hasattr(obj, 'libraries') else []
    #     return LibrarySerializer(libraries, many=True).data


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'

class PublishingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publishing
        fields = '__all__'

class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = '__all__'

class ContributionSerializer(serializers.ModelSerializer):
    # Nested serializers for related objects to access in the contribution api endpoint
    class Meta:
        model = Contribution
        fields = '__all__'

class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = '__all__'

class SocialMediaLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaLink
        fields = '__all__'

class MusicProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicProfessional
        fields = '__all__'

class FileFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileFormat
        fields = '__all__'

class TrackStorageFileSerializer(serializers.ModelSerializer):
    file_format = FileFormatSerializer(read_only=True)  # Nest the format
    class Meta:
        model = TrackStorageFile
        fields = '__all__'

    
    