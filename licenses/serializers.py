from rest_framework import serializers
from .models import Copyright, CopyrightHolding, CopyrightStatus, License, LicenseHolding, LicenseStatus, License_type, Licensee, TrackLicenseOptions
from music.serializers import TrackStorageFileSerializer
# Serializers for Copyright, CopyrightHolding, License, LicenseHolding, LicenseStatus
class CopyrightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Copyright
        fields = '__all__'

class CopyrightHoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CopyrightHolding
        fields = '__all__'

class CopyrightStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CopyrightStatus
        fields = '__all__'

class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = '__all__'

class LicenseHoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseHolding
        fields = '__all__'

class LicenseStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseStatus
        fields = '__all__'

class LicenseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = License_type
        fields = '__all__'

class LicenseeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Licensee
        fields = '__all__'

class TrackLicenseOptionsSerializer(serializers.ModelSerializer):
    track_storage_file = TrackStorageFileSerializer(read_only=True)
    license_type = LicenseTypeSerializer(read_only=True)
    class Meta:
        model = TrackLicenseOptions
        fields = '__all__'
    # # I need to access the license types directly from the track model in the front end
    # def get_license_types(self, obj):
    #     from licenses.serializers import LicenseTypeSerializer  # Import here to avoid circular imports
    #     license_types = obj.license_types.all()
    #     return LicenseTypeSerializer(license_types, many=True).data
    # def get_track_storage_file(self, obj):
    #     from music.serializers import TrackStorageFileSerializer  # Import here to avoid circular imports
    #     track_storage_file = obj.track_storage_file
    #     return TrackStorageFileSerializer(track_storage_file).data    
    
        
    
    