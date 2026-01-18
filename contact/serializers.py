from rest_framework import serializers
from .models import ContactSubmission

class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    social_media_link_1 = serializers.URLField(required=False, allow_blank=True)
    social_media_link_2 = serializers.URLField(required=False, allow_blank=True)
    services_required = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'Production', 'Mixing', 'Mastering', 'Recording', 'Other'
        ]),
        allow_empty=False
    )
    message = serializers.CharField(max_length=5000)
    attachment = serializers.FileField(required=False, allow_empty_file=True)
    recaptcha_token = serializers.CharField(max_length=1000)

    # Allowed MIME types
    ALLOWED_TYPES = ['application/pdf', 'audio/mpeg', 'audio/mp3']
    MAX_SIZE_BYTES = 25 * 1024 * 1024  # 25MB

    def validate_attachment(self, value):
        if not value:
            return value

        # Check file size
        if value.size > self.MAX_SIZE_BYTES:
            raise serializers.ValidationError("Attachment cannot exceed 25MB.")

        # Check MIME type
        if value.content_type not in self.ALLOWED_TYPES:
            raise serializers.ValidationError(
                f"Only PDF and MP3 files are allowed. Got: {value.content_type}"
            )
        return value