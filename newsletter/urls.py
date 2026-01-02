from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsletterCategoryViewSet, SubscribeView, UnsubscribeView

router = DefaultRouter()
router.register(r'categories', NewsletterCategoryViewSet, basename='newsletter-category')

urlpatterns = [
    path('newsletter/', include(router.urls)),
    path('newsletter/subscribe/', SubscribeView.as_view(), name='newsletter-subscribe'),
    path('newsletter/unsubscribe/', UnsubscribeView.as_view(), name='newsletter-unsubscribe'),
]