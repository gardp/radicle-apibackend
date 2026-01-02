from rest_framework import serializers
from .models import NewsletterCategory, Subscriber, Subscription


class NewsletterCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterCategory
        fields = ['category_id', 'name', 'slug', 'description']


class SubscribeSerializer(serializers.Serializer):
    """Serializer for the subscribe endpoint."""
    email = serializers.EmailField()
    source = serializers.ChoiceField(
        choices=Subscription.SubscriptionSource.choices,
        default=Subscription.SubscriptionSource.WEBSITE_FOOTER
    )
    categories = serializers.ListField(
        child=serializers.SlugField(),
        required=False,
        help_text="List of category slugs. If empty, subscribes to default categories."
    )

    def validate_email(self, value):
        return value.lower().strip()


class SubscriberSerializer(serializers.ModelSerializer):
    subscriptions = serializers.SerializerMethodField()

    class Meta:
        model = Subscriber
        fields = ['subscriber_id', 'email', 'is_active', 'subscribed_at', 'subscriptions']
        read_only_fields = ['subscriber_id', 'subscribed_at']

    def get_subscriptions(self, obj):
        active_subs = obj.subscriptions.filter(is_active=True)
        return [sub.category.slug for sub in active_subs]


class UnsubscribeSerializer(serializers.Serializer):
    """Serializer for unsubscribe endpoint."""
    email = serializers.EmailField()
    token = serializers.UUIDField()
    categories = serializers.ListField(
        child=serializers.SlugField(),
        required=False,
        help_text="Specific categories to unsubscribe from. If empty, unsubscribes from all."
    )