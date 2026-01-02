from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import NewsletterCategory, Subscriber, Subscription
from .serializers import (
    NewsletterCategorySerializer,
    SubscribeSerializer,
    SubscriberSerializer,
    UnsubscribeSerializer,
)


class NewsletterCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """List available newsletter categories."""
    queryset = NewsletterCategory.objects.filter(is_active=True)
    serializer_class = NewsletterCategorySerializer
    permission_classes = [permissions.AllowAny]


class SubscribeView(APIView):
    """
    POST /api/v1/newsletter/subscribe/
    
    Subscribe an email to the newsletter.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        source = serializer.validated_data['source']
        category_slugs = serializer.validated_data.get('categories', [])

        # Get or create subscriber
        subscriber, created = Subscriber.objects.get_or_create(
            email=email
        )

        # If subscriber was inactive, reactivate
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.unsubscribed_at = None
            subscriber.save()

        # Determine categories to subscribe to
        if category_slugs:
            categories = NewsletterCategory.objects.filter(
                slug__in=category_slugs,
                is_active=True
            )
        else:
            # Subscribe to default categories
            categories = NewsletterCategory.objects.filter(
                is_default=True,
                is_active=True
            )

        # Create subscriptions
        for category in categories:
            Subscription.objects.get_or_create(
                subscriber=subscriber,
                category=category,
                defaults={'is_active': True, 'source': source}
            )

        # 🆕 Send confirmation email (only for new subscribers)
        if created:
            from .tasks import send_subscription_confirmation_email
            send_subscription_confirmation_email.delay(subscriber.subscriber_id)

        return Response({
            'message': 'Successfully subscribed to newsletter',
            'email': email,
            'categories': [cat.name for cat in categories],
            'is_new': created
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class UnsubscribeView(APIView):
    """
    POST /api/v1/newsletter/unsubscribe/
    
    Unsubscribe from newsletter (requires token for security).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UnsubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower().strip()
        token = serializer.validated_data['token']
        category_slugs = serializer.validated_data.get('categories', [])

        # Find subscriber with matching email and token
        subscriber = get_object_or_404(
            Subscriber,
            email=email,
            unsubscribe_token=token
        )

        if category_slugs:
            # Unsubscribe from specific categories
            Subscription.objects.filter(
                subscriber=subscriber,
                category__slug__in=category_slugs
            ).update(is_active=False)
            message = f"Unsubscribed from: {', '.join(category_slugs)}"
        else:
            # Unsubscribe from all
            subscriber.unsubscribe_all()
            message = "Unsubscribed from all newsletters"

        return Response({'message': message})

    def get(self, request):
        """
        GET /api/v1/newsletter/unsubscribe/?email=...&token=...
        
        Alternative GET method for email link clicks.
        """
        email = request.query_params.get('email', '').lower().strip()
        token = request.query_params.get('token', '')

        if not email or not token:
            return Response(
                {'error': 'Email and token are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            subscriber = Subscriber.objects.get(email=email, unsubscribe_token=token)
            subscriber.unsubscribe_all()
            return Response({'message': 'Successfully unsubscribed from all newsletters'})
        except Subscriber.DoesNotExist:
            return Response(
                {'error': 'Invalid unsubscribe link'},
                status=status.HTTP_404_NOT_FOUND
            )