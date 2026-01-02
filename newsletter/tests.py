from django.test import TestCase
from django.core import mail
from django.utils import timezone
from .models import Newsletter, NewsletterCategory, Subscriber, Subscription
from .tasks import send_newsletter_task
import uuid

class NewsletterTests(TestCase):
    def setUp(self):
        # Create category
        self.category = NewsletterCategory.objects.create(
            name="Weekly Updates",
            slug="weekly-updates"
        )
        
        # Create subscribers
        self.sub1 = Subscriber.objects.create(email="sub1@example.com", is_active=True)
        self.sub2 = Subscriber.objects.create(email="sub2@example.com", is_active=True)
        self.sub3 = Subscriber.objects.create(email="sub3@example.com", is_active=False) # Inactive
        
        # Subscribe them
        Subscription.objects.create(subscriber=self.sub1, category=self.category)
        Subscription.objects.create(subscriber=self.sub2, category=self.category)

    def test_send_newsletter_all_active(self):
        """Test sending newsletter to all active subscribers."""
        newsletter = Newsletter.objects.create(
            subject="Test Newsletter",
            content="<p>Hello World</p>"
        )
        
        # Run task synchronously
        count = send_newsletter_task(newsletter.newsletter_id)
        
        self.assertEqual(count, 2) # sub1 and sub2
        self.assertEqual(len(mail.outbox), 2)
        
        # Verify status update
        newsletter.refresh_from_db()
        self.assertEqual(newsletter.status, Newsletter.Status.SENT)
        self.assertIsNotNone(newsletter.sent_at)
        
        # Verify content has unsubscribe link
        # We sent 2 emails, order is not guaranteed. Find the one for sub1.
        email_body_sub1 = None
        for message in mail.outbox:
            if self.sub1.email in message.to:
                email_body_sub1 = message.alternatives[0][0]
                break
        
        self.assertIsNotNone(email_body_sub1)
        self.assertIn("Unsubscribe", email_body_sub1)
        self.assertIn(str(self.sub1.unsubscribe_token), email_body_sub1)

    def test_send_newsletter_targeted(self):
        """Test sending newsletter to a specific category."""
        # Create another category and subscriber
        other_cat = NewsletterCategory.objects.create(name="Promos", slug="promos")
        sub4 = Subscriber.objects.create(email="sub4@example.com", is_active=True)
        Subscription.objects.create(subscriber=sub4, category=other_cat)
        
        newsletter = Newsletter.objects.create(
            subject="Targeted Newsletter",
            content="Targeted Content",
            target_category=self.category
        )
        
        count = send_newsletter_task(newsletter.newsletter_id)
        
        self.assertEqual(count, 2) # Only sub1 and sub2 (in Weekly Updates)
        # sub4 is in Promos, sub3 is inactive
