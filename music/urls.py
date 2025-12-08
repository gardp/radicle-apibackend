# music/urls.py (Example)
from django.urls import path
from rest_framework import routers
from .views import TrackViewSet, PublisherViewSet, ContributorViewSet, LibraryViewSet, ContributionViewSet, PublishingViewSet, FileFormatViewSet, TrackStorageFileViewSet, MusicProfessionalViewSet, SocialMediaLinkViewSet, FileFormatViewSet
from django.urls import include

router = routers.DefaultRouter()
router.register(r'tracks', TrackViewSet, basename='tracks')
router.register(r'file-formats', FileFormatViewSet, basename='file-formats')
router.register(r'track-storage-files', TrackStorageFileViewSet, basename='track-storage-files')
router.register(r'music-professionals', MusicProfessionalViewSet, basename='music-professionals')
router.register(r'contributors', ContributorViewSet, basename='contributors')
router.register(r'social-media-links', SocialMediaLinkViewSet, basename='social-media-links')
router.register(r'contributions', ContributionViewSet, basename='contributions')
router.register(r'libraries', LibraryViewSet, basename='libraries')
router.register(r'publishers', PublisherViewSet, basename='publishers')
router.register(r'publishings', PublishingViewSet, basename='publishings')
urlpatterns = [
    path('', include(router.urls)),
    # You might have custom paths here too
]

# List: Get all tracks (GET /tracks/)
# Create: Add a new track (POST /tracks/)
# Retrieve: Get a specific track by ID (GET /tracks/{id}/)
# Update: Modify a specific track (PUT /tracks/{id}/, PATCH /tracks/{id}/)
# Destroy: Delete a specific track (DELETE /tracks/{id}/)

# GET	/tracks/	List all tracks	tracks-list
# POST	/tracks/	Create a new track	tracks-list
# GET	/tracks/{id}/	Retrieve a specific track	tracks-detail
# PUT	/tracks/{id}/	Update a specific track	tracks-detail
# PATCH	/tracks/{id}/	Partially update a track	tracks-detail
# DELETE	/tracks/{id}/	Delete a specific track	tracks-detail
