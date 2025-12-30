import logging
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import get_connection
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.core.mail.message import EmailMessage
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class SendGridBackend:
    """SendGrid email backend for production use."""
    
    def __init__(self, fail_silently=False, **kwargs):
        self.api_key = getattr(settings, 'SENDGRID_API_KEY', None)
        self.from_email = getattr(settings, 'SENDGRID_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        self.fail_silently = fail_silently
        
        if not self.api_key:
            raise ImproperlyConfigured("SENDGRID_API_KEY is required for SendGrid backend")
    
    def send_messages(self, email_messages):
        """
        Send email messages via SendGrid API.
        Returns number of successfully sent messages.
        """
        if not email_messages:
            return 0
            
        sent_count = 0
        
        for message in email_messages:
            try:
                # Extract HTML content
                html_content = getattr(message, 'html_body', None)
                if not html_content and hasattr(message, 'alternatives'):
                    for content, mimetype in message.alternatives:
                        if mimetype == 'text/html':
                            html_content = content
                            break

                # Create SendGrid message
                sg_message = Mail(
                    from_email=self.from_email,
                    to_emails=message.to,
                    subject=message.subject,
                    html_content=html_content or message.body,
                )
                
                # Add CC and BCC if present
                if message.cc:
                    sg_message.cc = message.cc
                if message.bcc:
                    sg_message.bcc = message.bcc
                
                # Add reply-to if present
                if message.reply_to:
                    # SendGrid helper expects a single email or ReplyTo object
                    # Django uses a list for reply_to
                    if isinstance(message.reply_to, list) and message.reply_to:
                        sg_message.reply_to = message.reply_to[0]
                    else:
                        sg_message.reply_to = message.reply_to
                
                # Send via SendGrid API
                sg = SendGridAPIClient(self.api_key)
                response = sg.send(sg_message)
                
                if response.status_code in [200, 202]:
                    sent_count += 1
                    logger.info(f"SendGrid sent email to {message.to}")
                else:
                    logger.error(f"SendGrid failed: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"SendGrid error sending to {message.to}: {str(e)}")
                if not self.fail_silently:
                    raise
        
        return sent_count


class HybridEmailBackend:
    """
    Hybrid email backend that tries SendGrid first, falls back to SMTP.
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self.sendgrid_backend = None
        self.smtp_backend = None
        
        # Initialize SendGrid backend if API key is available
        if getattr(settings, 'SENDGRID_API_KEY', None):
            try:
                self.sendgrid_backend = SendGridBackend(fail_silently=True, **kwargs)
            except ImproperlyConfigured:
                logger.warning("SendGrid not configured, using SMTP only")
        
        # Initialize SMTP backend as fallback
        self.smtp_backend = EmailBackend(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
            fail_silently=self.fail_silently,  # Respect the fail_silently argument
        )
    
    def send_messages(self, email_messages):
        """
        Try SendGrid first, fall back to SMTP if it fails.
        Attempts to send each message individually via SendGrid, 
        and falls back to SMTP for any that fail.
        """
        if not email_messages:
            return 0
        
        sent_count = 0
        
        for message in email_messages:
            message_sent = False
            
            # Try SendGrid first
            if self.sendgrid_backend:
                try:
                    # SendGridBackend.send_messages expects a list
                    sg_count = self.sendgrid_backend.send_messages([message])
                    if sg_count == 1:
                        sent_count += 1
                        message_sent = True
                        logger.info(f"Email to {message.to} sent via SendGrid")
                except Exception as e:
                    logger.warning(f"SendGrid failed for {message.to}: {str(e)}, falling back to SMTP")
            
            # Fallback to SMTP if SendGrid failed or wasn't available
            if not message_sent and self.smtp_backend:
                try:
                    # SMTP backend also expects a list
                    smtp_count = self.smtp_backend.send_messages([message])
                    if smtp_count == 1:
                        sent_count += 1
                        logger.info(f"Email to {message.to} sent via SMTP fallback")
                except Exception as e:
                    logger.error(f"SMTP fallback failed for {message.to}: {str(e)}")
                    if not self.fail_silently:
                        raise
        
        return sent_count