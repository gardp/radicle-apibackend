from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from .models import Newsletter, Subscriber
import logging

logger = logging.getLogger(__name__)

# Send newsletter to subscribers
@shared_task
def send_newsletter_task(newsletter_id):
    """
    Celery task to send a newsletter to all eligible subscribers.
    """
    try:
        newsletter = Newsletter.objects.get(newsletter_id=newsletter_id)
    except Newsletter.DoesNotExist:
        logger.error(f"Newsletter {newsletter_id} not found.")
        return

    # Update status to indicate processing (optional, or just keep as DRAFT until done)
    # For now, we'll update to SENT at the end.

    # Filter subscribers
    subscribers = Subscriber.objects.filter(is_active=True)
    if newsletter.target_category:
        # Filter by category subscription
        subscribers = subscribers.filter(
            subscriptions__category=newsletter.target_category,
            subscriptions__is_active=True
        )

    sent_count = 0
    base_url = getattr(settings, 'PUBLIC_BASE_URL', 'http://localhost:8000')

    for subscriber in subscribers:
        try:
            # Generate unsubscribe link
            unsubscribe_url = f"{base_url}/newsletter/unsubscribe/{subscriber.unsubscribe_token}/"
            
            # Append unsubscribe link to content
            # Simple append for now. In a real app, you might want a proper HTML template.
            html_content = newsletter.content + f'<br><br><hr><p><small><a href="{unsubscribe_url}">Unsubscribe</a></small></p>'
            
            # Create email
            msg = EmailMultiAlternatives(
                subject=newsletter.subject,
                body=html_content, # Text content fallback could be stripped HTML
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subscriber.email]
            )
            msg.attach_alternative(html_content, "text/html")
            
            # Send
            msg.send()
            sent_count += 1
            
        except Exception as e:
            logger.error(f"Failed to send newsletter {newsletter.subject} to {subscriber.email}: {str(e)}")

    # Update newsletter status
    newsletter.status = Newsletter.Status.SENT
    newsletter.sent_at = timezone.now()
    newsletter.save()

    logger.info(f"Newsletter {newsletter.subject} sent to {sent_count} subscribers.")
    return sent_count

# Send confirmation email to new subscribers
@shared_task
def send_subscription_confirmation_email(subscriber_id):
    print("Sending confirmation email to subscriber", subscriber_id)
    """Send a welcome/confirmation email to a new subscriber."""
    try:
        subscriber = Subscriber.objects.get(subscriber_id=subscriber_id)
    except Subscriber.DoesNotExist:
        logger.error(f"Subscriber {subscriber_id} not found.")
        return

    # Build confirmation/welcome message
    from core.email_service import EmailService
    
    # Get category names they subscribed to
    categories = subscriber.subscriptions.filter(is_active=True).values_list('category__name', flat=True)
    
    EmailService.send_transactional_email(
        subject="Welcome to Our Newsletter!",
        recipient_list=[subscriber.email],
        template_name="emails/newsletter_confirmation",  # Create this template
        context={
            'categories': list(categories),
            'unsubscribe_url': f"{settings.PUBLIC_BASE_URL}/api/v1/newsletter/unsubscribe/?email={subscriber.email}&token={subscriber.unsubscribe_token}"
        }
    )