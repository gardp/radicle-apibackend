from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from .models import ContactSubmission
from .utils.recaptcha import verify_recaptcha
from .utils.rate_limiter import check_rate_limit
from .tasks import send_contact_emails
import logging

logger = logging.getLogger(__name__)

class ContactView(APIView):
    permission_classes = []  # Allow any
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        # Get client IP
        ip_address = self.get_client_ip(request)
        
        # Rate limiting check
        allowed, remaining, reset_time = check_rate_limit(ip_address)
        if not allowed:
            return Response(
                {'error': 'Rate limit exceeded', 'reset_time': reset_time},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Get raw data directly (no serializer)
        data = request.data
        
        # Manual validation
        name = data.get('name')
        email = data.get('email')
        social_media_link_1 = data.get('socialMediaLink1', '')
        social_media_link_2 = data.get('socialMediaLink2', '')
        services_required = data.get('servicesRequired')
        try:
            import json
            services_dict = json.loads(services_required)
            selected_services = [service.capitalize() for service, checked in services_dict.items() if checked]
        except(json.JSONDecodeError, AttributeError):
            services_required = []
        services_required_other = data.get('servicesRequiredOther', '')
        additional_info = data.get('additionalInfo', '')
        recaptcha_token = data.get('recaptchaToken')
        attachment = data.get('file')
        
        # Manual validation checks
        if not name or not email or not services_required or not recaptcha_token:
            return Response(
                {'error': 'Missing required fields'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify reCAPTCHA
        recaptcha_success, recaptcha_error = verify_recaptcha(recaptcha_token, ip_address)
        if not recaptcha_success:
            return Response(
                {'error': 'reCAPTCHA verification failed', 'detail': recaptcha_error},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create submission record
        submission = ContactSubmission.objects.create(
            email=email,
            ip_address=ip_address,
            attachment=attachment
        )

        # Prepare payload for Celery
        payload = {
            'name': name,
            'email': email,
            'social_media_link_1': social_media_link_1,
            'social_media_link_2': social_media_link_2,
            'services_required': selected_services,
            'services_required_other': services_required_other,
            'additional_info': additional_info
        }

        # Enqueue email task
        send_contact_emails.delay(str(submission.id), payload)

        return Response(
            {'message': 'Your message has been received. We will get back to you soon.'},
            status=status.HTTP_201_CREATED
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip