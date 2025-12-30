
import os
import sys
import logging
from unittest.mock import MagicMock, patch
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives

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
        SENDGRID_FROM_EMAIL='test@example.com',
        DEFAULT_FROM_EMAIL='webmaster@example.com',
    )

import django
django.setup()

from core.email_backends import SendGridBackend, HybridEmailBackend

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sendgrid_backend_html_attribute_error():
    print("\n--- Testing SendGridBackend Attribute Error ---")
    
    # Mock SendGridAPIClient to avoid real network calls
    with patch('core.email_backends.SendGridAPIClient') as MockSG:
        mock_sg = MockSG.return_value
        mock_sg.send.return_value.status_code = 202
        
        backend = SendGridBackend()
        
        # Create a standard EmailMessage (no html_body attribute)
        msg = EmailMessage(
            subject="Test Subject",
            body="Test Body",
            from_email="test@example.com",
            to=["recipient@example.com"]
        )
        
        try:
            backend.send_messages([msg])
            print("SUCCESS: SendGridBackend handled standard EmailMessage without AttributeError")
        except AttributeError as e:
            print(f"FAIL: Caught AttributeError: {e}")
        except Exception as e:
            print(f"FAIL: Caught unexpected exception: {type(e).__name__}: {e}")

def test_hybrid_backend_double_sending():
    print("\n--- Testing HybridBackend Double Sending ---")
    
    # Mock SendGridBackend
    with patch('core.email_backends.SendGridBackend') as MockSendGridBackend:
        mock_sg_instance = MockSendGridBackend.return_value
        
        # Setup side_effect to simulate success for first msg, failure for second
        # The backend now calls send_messages with a list of 1 message
        def sg_side_effect(messages):
            if messages[0].subject == "Msg 1":
                return 1
            return 0 # Fail for Msg 2
            
        mock_sg_instance.send_messages.side_effect = sg_side_effect
        
        # Mock SMTP backend
        with patch('core.email_backends.EmailBackend') as MockSMTPBackend:
            mock_smtp_instance = MockSMTPBackend.return_value
            mock_smtp_instance.send_messages.return_value = 1 # SMTP succeeds
            
            backend = HybridEmailBackend()
            
            msg1 = EmailMessage(subject="Msg 1", body="Body 1", to=["r1@example.com"])
            msg2 = EmailMessage(subject="Msg 2", body="Body 2", to=["r2@example.com"])
            
            print("Sending 2 messages...")
            sent_count = backend.send_messages([msg1, msg2])
            print(f"Total sent count: {sent_count}")
            
            # Verification
            # SG called twice (once for each)
            print(f"SendGrid called {mock_sg_instance.send_messages.call_count} times")
            
            # SMTP called once (only for the failed one)
            print(f"SMTP called {mock_smtp_instance.send_messages.call_count} times")
            
            if mock_smtp_instance.send_messages.call_count == 1:
                # Check it was called with Msg 2
                args = mock_smtp_instance.send_messages.call_args[0][0]
                if len(args) == 1 and args[0].subject == "Msg 2":
                    print("SUCCESS: SMTP sent ONLY the failed message")
                else:
                    print(f"FAIL: SMTP called with wrong args: {args}")
            else:
                print(f"FAIL: SMTP called {mock_smtp_instance.send_messages.call_count} times (expected 1)")

if __name__ == "__main__":
    test_sendgrid_backend_html_attribute_error()
    test_hybrid_backend_double_sending()
