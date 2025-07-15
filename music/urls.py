# music/urls.py (Example)
from django.urls import path
from rest_framework import routers
from .views import TrackViewSet
from django.urls import include

router = routers.DefaultRouter()
router.register(r'tracks', TrackViewSet)
# router.register(r'library', LibraryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # You might have custom paths here too
]

# List: Get all tracks (GET /tracks/)
# Create: Add a new track (POST /tracks/)
# Retrieve: Get a specific track by ID (GET /tracks/{id}/)
# Update: Modify a specific track (PUT /tracks/{id}/, PATCH /tracks/{id}/)
# Destroy: Delete a specific track (DELETE /tracks/{id}/)