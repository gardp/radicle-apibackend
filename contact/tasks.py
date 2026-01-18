from celery import shared_task
from django.core.files.base import ContentFile
from django.conf import settings
from .models import ContactSubmission
from core.email_service import EmailService
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_contact_emails(self, submission_id, payload):
    """
    Send contact us emails (to host and user) asynchronously.
    Payload contains only text fields; attachment is loaded from the model.
    """
    try:
        submission = ContactSubmission.objects.get(id=submission_id)
    except ContactSubmission.DoesNotExist:
        logger.error(f"ContactSubmission {submission_id} not found")
        return

    try:
        # Prepare attachment if present
        attachments = []
        if submission.attachment:
            submission.attachment.open('rb')
            content = submission.attachment.read()
            submission.attachment.close()
            filename = submission.attachment.name.split('/')[-1]
            # Get content_type properly
            content_type = submission.attachment.file.content_type if hasattr(submission.attachment.file, 'content_type') else 'application/octet-stream'
            attachments.append((filename, content, content_type))   

        # Send email to host with attachment
        EmailService.send_transactional_email(
            subject=f"New Contact Request: {payload['name']}",
            message=(
                f"Name: {payload['name']}\n"
                f"Email: {payload['email']}\n"
                f"Social Link 1: {payload.get('social_media_link_1', 'N/A')}\n"
                f"Social Link 2: {payload.get('social_media_link_2', 'N/A')}\n"
                f"Services Required: {', '.join(payload['services_required'])}\n"
                f"Message:\n{payload['additional_info']}"
            ),
            recipient_list=[settings.CONTACT_RECEIVER_EMAIL],
            reply_to=[payload['email']],
            attachments=attachments
        )

        # Send confirmation email to user (no attachment)
        EmailService.send_transactional_email(
            subject="We received your message",
            message=(
                f"Hi {payload['name']},\n\n"
                "Thank you for contacting us. We've received your message and will get back to you soon.\n\n"
                "Best regards,\n"
                "RadicleSound"
            ),
            recipient_list=[payload['email']]
        )

        # Update status to success
        submission.status = ContactSubmission.Status.SUCCESS
        submission.save(update_fields=['status'])

        # Clean up attachment file
        if submission.attachment:
            submission.attachment.delete(save=False)

        logger.info(f"Contact emails sent successfully for {payload['email']}")

    except Exception as exc:
        logger.error(f"Failed to send contact emails for {payload['email']}: {exc}")
        submission.status = ContactSubmission.Status.FAILED
        submission.save(update_fields=['status'])
        raise self.retry(exc=exc, countdown=60)