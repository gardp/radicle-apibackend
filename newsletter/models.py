import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class NewsletterCategory(models.Model):
    """Categories for newsletter subscriptions."""
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(
        default=False,
        help_text="If True, new subscribers are automatically subscribed to this category."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Newsletter Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Subscriber(models.Model):
    """Newsletter subscriber - can be linked to a user or standalone."""
    
    class SubscriptionSource(models.TextChoices):
        WEBSITE_FOOTER = 'FOOTER', 'Website Footer'
        CHECKOUT = 'CHECKOUT', 'Checkout'
        REGISTRATION = 'REGISTRATION', 'User Registration'
        MANUAL = 'MANUAL', 'Manual Entry'
        OTHER = 'OTHER', 'Other'

    subscriber_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    
    # Optional link to registered user
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='newsletter_subscriber'
    )
    
    # Metadata
    source = models.CharField(
        max_length=20,
        choices=SubscriptionSource.choices,
        default=SubscriptionSource.WEBSITE_FOOTER
    )
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Secure token for unsubscribe links
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, editable=False)
    
    # Timestamps
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email

    def unsubscribe_all(self):
        """Unsubscribe from all categories."""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()
        self.subscriptions.update(is_active=False)


class Subscription(models.Model):
    """Links a subscriber to a specific newsletter category."""
    subscription_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscriber = models.ForeignKey(
        Subscriber,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    category = models.ForeignKey(
        NewsletterCategory,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['subscriber', 'category']
        ordering = ['-subscribed_at']

    def __str__(self):
        return f"{self.subscriber.email} -> {self.category.name}"