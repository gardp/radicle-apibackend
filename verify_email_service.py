
import os
import sys
import logging
from unittest.mock import MagicMock, patch
from django.conf import settings

# Configure minimal Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        EMAIL_HOST='smtp.example.com',
        EMAIL_PORT=587,
        EMAIL_HOST_USER='user',
        EMAIL_HOST_PASSWORD='password',
        EMAIL_USE_TLS=True,
        SENDGRID_API_KEY='sg.test.key',
        DEFAULT_FROM_EMAIL='webmaster@example.com',
        EMAIL_BACKEND_TYPE='hybrid',
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(os.getcwd(), 'core/templates')],
            'APP_DIRS': True,
        }],
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'core',
        ]
    )

import django
django.setup()

from core.email_service import EmailService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_send_transactional_email_with_template():
    print("\n--- Testing EmailService with Template and Attachments ---")
    
    # Mock EmailMultiAlternatives to verify calls
    with patch('django.core.mail.EmailMultiAlternatives') as MockEmail:
        mock_email_instance = MockEmail.return_value
        mock_email_instance.send.return_value = 1
        
        # Test data
        context = {
            'order_reference': 'ORDER-123',
            'licenses': [
                {'track_title': 'Track 1', 'track_url': 'http://dl.com/t1', 'license_url': 'http://dl.com/l1'}
            ]
        }
        attachments = [('license.pdf', b'pdf content', 'application/pdf')]
        
        # Call the service
        EmailService.send_transactional_email(
            subject="Test Subject",
            recipient_list=["test@example.com"],
            template_name="emails/license_email", # Relative to template dir
            context=context,
            attachments=attachments
        )
        
        # Verify EmailMultiAlternatives initialization
        args, kwargs = MockEmail.call_args
        print(f"Subject: {kwargs.get('subject')}")
        print(f"To: {kwargs.get('to')}")
        
        # Verify body (text content)
        body = kwargs.get('body')
        if "Order Reference: ORDER-123" in body and "Track: Track 1" in body:
            print("SUCCESS: Text body rendered correctly")
        else:
            print(f"FAIL: Text body incorrect: {body}")
            
        # Verify HTML alternative
        # attach_alternative is called with (content, mimetype)
        if mock_email_instance.attach_alternative.called:
            html_content = mock_email_instance.attach_alternative.call_args[0][0]
            if "<strong>ORDER-123</strong>" in html_content and "Track 1" in html_content:
                print("SUCCESS: HTML content rendered correctly")
            else:
                print(f"FAIL: HTML content incorrect: {html_content}")
        else:
            print("FAIL: attach_alternative not called")
            
        # Verify attachments
        if mock_email_instance.attach.called:
            att_args = mock_email_instance.attach.call_args[0]
            if att_args == ('license.pdf', b'pdf content', 'application/pdf'):
                print("SUCCESS: Attachment added correctly")
            else:
                print(f"FAIL: Attachment incorrect: {att_args}")
        else:
            print("FAIL: attach not called")

if __name__ == "__main__":
    # Create dummy template directory structure for test if needed, 
    # but we are pointing to actual files in core/templates
    # We need to make sure the path in settings matches where we are running
    
    # Adjust template dir to be absolute path to core/templates
    current_dir = os.getcwd()
    template_dir = os.path.join(current_dir, 'core/templates')
    settings.TEMPLATES[0]['DIRS'] = [template_dir]
    
    test_send_transactional_email_with_template()
