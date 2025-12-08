from django.shortcuts import render
from rest_framework import generics 
from .models import Copyright, CopyrightHolding, CopyrightStatus, License, Licensee, LicenseHolding, LicenseStatus, License_type, TrackLicenseOptions
from .serializers import CopyrightSerializer, CopyrightHoldingSerializer, CopyrightStatusSerializer, LicenseSerializer, LicenseeSerializer, LicenseHoldingSerializer, LicenseStatusSerializer, LicenseTypeSerializer, TrackLicenseOptionsSerializer
from rest_framework import viewsets 
from rest_framework import permissions  
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from .models import License
from django.http import FileResponse

# Create your views here.
class CopyrightViewSet(viewsets.ModelViewSet):
    queryset = Copyright.objects.all()
    serializer_class = CopyrightSerializer
    permission_classes = [permissions.AllowAny]

class CopyrightHoldingViewSet(viewsets.ModelViewSet):
    queryset = CopyrightHolding.objects.all()
    serializer_class = CopyrightHoldingSerializer
    permission_classes = [permissions.AllowAny]

class CopyrightStatusViewSet(viewsets.ModelViewSet):
    queryset = CopyrightStatus.objects.all()
    serializer_class = CopyrightStatusSerializer
    permission_classes = [permissions.AllowAny]

class LicenseViewSet(viewsets.ModelViewSet):
    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    permission_classes = [permissions.AllowAny]


class LicenseeViewSet(viewsets.ModelViewSet):
    queryset = Licensee.objects.all()
    serializer_class = LicenseeSerializer
    permission_classes = [permissions.AllowAny]

class LicenseHoldingViewSet(viewsets.ModelViewSet):
    queryset = LicenseHolding.objects.all()
    serializer_class = LicenseHoldingSerializer
    permission_classes = [permissions.AllowAny]

class LicenseStatusViewSet(viewsets.ModelViewSet):
    queryset = LicenseStatus.objects.all()
    serializer_class = LicenseStatusSerializer
    permission_classes = [permissions.AllowAny]


class LicenseTypeViewSet(viewsets.ModelViewSet):
    queryset = License_type.objects.all()
    serializer_class = LicenseTypeSerializer
    permission_classes = [permissions.AllowAny]
    
class TrackLicenseOptionsViewSet(viewsets.ModelViewSet): 
    queryset = TrackLicenseOptions.objects.all()
    serializer_class = TrackLicenseOptionsSerializer
    permission_classes = [permissions.AllowAny]
    
# for track_id in the list view is already covered.
    def get_queryset(self):
        return TrackLicenseOptions.objects.all()

    @action(detail=False, methods=['get'], url_path='by-track/(?P<track_pk>[^/.]+)')
    def get_by_track(self, request, track_pk=None):
        """
        Retrieves all TrackLicenseOptions associated with a specific Track ID.
        """
        # 1. Use filter() because a single track can have MULTIPLE license options.
        #    If you used .get(), it would crash if the track had >1 license option.
        try:
            queryset = self.get_queryset().filter(track_id=track_pk)
            
            # If you expect only ONE result per track, use .get(), 
            # but your schema suggests many are possible.
            # If no results, return 404.
            if not queryset.exists():
                return Response(
                    {'detail': f'No license options found for track ID: {track_pk}'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 2. Serialize the (potentially) multiple objects.
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        except Exception:
            # Handle cases where the track_pk format is invalid (e.g., not a valid UUID)
             return Response(
                {'detail': 'Invalid track ID format.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

# function that will be sent with the link in url to download the license agreement
def download_license_agreement(request, license_id):
    license_obj = get_object_or_404(License, pk=license_id)

    if not license_obj.license_agreement_file:
        raise Http404("License agreement file not found.")

    filename = f"license_{license_obj.license_id}.pdf"
    return FileResponse(
        license_obj.license_agreement_file.open("rb"),
        as_attachment=True,
        filename=filename,
    )

# function that will be sent with the link in url to download the track
def download_track(request, license_id):
    license_obj = get_object_or_404(License, pk=license_id)
    track_file_path = license_obj.track_license_option.track_storage_file.file_path

    if not track_file_path:
        raise Http404("Track file not found.")

    filename = f"track_{license_obj.track_license_option.track_storage_file.track_storage_file_id}.mp3"
    return FileResponse(
        track_file_path.open("rb"),
        as_attachment=True,
        filename=filename,
    )


    