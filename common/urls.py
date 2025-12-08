from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet
from .views import AddressViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='contacts')
router.register(r'addresses', AddressViewSet, basename='addresses')
# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
    