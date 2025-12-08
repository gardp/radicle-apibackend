# music/urls.py (Example)
from django.urls import path
from rest_framework import routers
from .views import CopyrightViewSet, CopyrightHoldingViewSet, CopyrightStatusViewSet, LicenseViewSet, LicenseHoldingViewSet, LicenseStatusViewSet, LicenseTypeViewSet, LicenseeViewSet, TrackLicenseOptionsViewSet, download_license_agreement, download_track
from django.urls import include

router = routers.DefaultRouter()
router.register(r'copyrights', CopyrightViewSet, basename='copyrights')
router.register(r'copyright-holdings', CopyrightHoldingViewSet, basename='copyright-holdings')
router.register(r'copyright-status', CopyrightStatusViewSet, basename='copyright-status')
router.register(r'licenses', LicenseViewSet, basename='licenses')
router.register(r'license-holdings', LicenseHoldingViewSet, basename='license-holdings')
router.register(r'license-status', LicenseStatusViewSet, basename='license-status')
router.register(r'license-types', LicenseTypeViewSet, basename='license-types')
router.register(r'licensees', LicenseeViewSet, basename='licensees')
router.register(r'track-license-options', TrackLicenseOptionsViewSet, basename='track-license-options')

urlpatterns = [
    path('', include(router.urls)),
    path(
        "download/license/<uuid:license_id>/",
        download_license_agreement,
        name="download-license",
    ),
    path(
        "download/track/<uuid:license_id>/",
        download_track,
        name="download-track",
    ),
]

# List: Get all tracks (GET /tracks/)
# Create: Add a new track (POST /tracks/)
# Retrieve: Get a specific track by ID (GET /tracks/{id}/)
# Update: Modify a specific track (PUT /tracks/{id}/, PATCH /tracks/{id}/)
# Destroy: Delete a specific track (DELETE /tracks/{id}/)

# GET	/copyrights/	List all copyrights	copyrights-list
# POST	/copyrights/	Create a new copyright	copyrights-list
# GET	/copyrights/{id}/	Retrieve a specific copyright	copyrights-detail
# PUT	/copyrights/{id}/	Update a specific copyright	copyrights-detail
# PATCH	/copyrights/{id}/	Partially update a copyright	copyrights-detail
# DELETE	/copyrights/{id}/	Delete a specific copyright	copyrights-detail