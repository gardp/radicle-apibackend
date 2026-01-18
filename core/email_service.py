import logging
from django.core.mail import get_connection, send_mail
from django.conf import settings
from .email_backends import SendGridBackend, HybridEmailBackend

logger = logging.getLogger(__name__)


class EmailService:
    """High-level email service with backend selection logic."""
    
    @staticmethod
    def send_newsletter(subject, message, recipient_list, html_message=None):
        """
        Send newsletter - optimized for bulk sending.
        Always tries to use SendGrid first for newsletters.
        """
        backend_type = 'sendgrid' if getattr(settings, 'SENDGRID_API_KEY', None) else settings.EMAIL_BACKEND_TYPE
        
        backend = get_connection()
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
                connection=backend
            )
            logger.info(f"Newsletter sent to {len(recipient_list)} recipients via {backend_type}")
        except Exception as e:
            logger.error(f"Newsletter sending failed: {str(e)}")
            raise
    
    @staticmethod
    def send_transactional_email(subject, message=None, recipient_list=None, html_message=None, 
                               template_name=None, context=None, attachments=None, reply_to=None):
        """
        Send transactional emails (license agreements, receipts, etc.).
        Uses hybrid backend for reliability.
        
        Args:
            subject (str): Email subject
            message (str): Plain text message (optional if template_name provided)
            recipient_list (list): List of recipient emails
            html_message (str): HTML content (optional if template_name provided)
            template_name (str): Path to template (without extension) for rendering both .txt and .html
            context (dict): Context for template rendering
            attachments (list): List of attachments. Each item can be:
                - A tuple (filename, content, mimetype)
                - An EmailAttachment object
            reply_to (list): List of reply-to emails
        """
        from django.template.loader import render_to_string
        from django.core.mail import EmailMultiAlternatives
        
        # Render templates if provided
        if template_name and context:
            if not message:
                try:
                    message = render_to_string(f"{template_name}.txt", context)
                except Exception:
                    # Fallback if txt template doesn't exist, though it should
                    pass
            
            if not html_message:
                try:
                    html_message = render_to_string(f"{template_name}.html", context)
                except Exception:
                    pass
        
        if not message and not html_message:
            raise ValueError("Either message/html_message OR template_name/context must be provided")
            
        # Create email object
        email = EmailMultiAlternatives(
            subject=subject,
            body=message or "",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
            reply_to=reply_to or []
        )
        
        # Attach HTML alternative
        if html_message:
            email.attach_alternative(html_message, "text/html")
            
        # Add attachments
        if attachments:
            for attachment in attachments:
                if isinstance(attachment, tuple):
                    email.attach(*attachment)
                else:
                    email.attach(attachment)
        
        try:
            email.send(fail_silently=False)
            logger.info(f"Transactional email sent to {recipient_list}")
        except Exception as e:
            logger.error(f"Transactional email failed to {recipient_list}: {str(e)}")
            raise
    
    @staticmethod
    def get_backend_info():
        """Return current email backend information."""
        return {
            'backend_type': settings.EMAIL_BACKEND_TYPE,
            'sendgrid_configured': bool(getattr(settings, 'SENDGRID_API_KEY', None)),
            'smtp_configured': bool(settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD),
        }