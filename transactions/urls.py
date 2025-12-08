from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderItemViewSet, PaymentViewSet, ReceiptViewSet, BuyerViewSet, ContentTypeMappingViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'buyers', BuyerViewSet, basename='buyers')    
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'order-items', OrderItemViewSet, basename='order-items')
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'receipts', ReceiptViewSet, basename='receipts')
router.register(r'content-type-mappings', ContentTypeMappingViewSet, basename='content-type-mappings')
# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]

# GET	/buyers/	List all buyers	buyers-list
# POST	/buyers/	Create a new buyer	buyers-list
# GET	/buyers/{id}/	Retrieve a specific buyer	buyers-detail
# PUT	/buyers/{id}/	Update a specific buyer	buyers-detail
# PATCH	/buyers/{id}/	Partially update a buyer	buyers-detail
# DELETE	/buyers/{id}/	Delete a specific buyer	buyers-detail
