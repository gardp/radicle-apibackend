from django.shortcuts import render
from rest_framework import generics 
from .models import Copyright, CopyrightHolding, CopyrightStatus, License, Licensee, LicenseHolding, LicenseStatus, License_type, TrackLicenseOptions, LicenseDownload
from .serializers import CopyrightSerializer, CopyrightHoldingSerializer, CopyrightStatusSerializer, LicenseSerializer, LicenseeSerializer, LicenseHoldingSerializer, LicenseStatusSerializer, LicenseTypeSerializer, TrackLicenseOptionsSerializer
from rest_framework import viewsets 
from rest_framework import permissions  
from .services import generate_license_agreement, build_download_urls, send_license_email
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from .models import License
from django.http import FileResponse
from django.utils import timezone
import os
from django.core.files.storage import default_storage
from django.conf import settings
from django.shortcuts import redirect

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

    @action(detail=True, methods=['post'], url_path='generate-agreement')
    def generate_agreement(self, request, pk=None):
        """
        Generate license agreement PDF for a specific license.
        POST /licenses/{license_id}/generate-agreement/
        """
        license_obj = self.get_object()
        
        if license_obj.license_agreement_file:
            return Response({
                'message': 'License agreement already exists',
                'license_id': str(license_obj.license_id),
                'file_url': license_obj.license_agreement_file.url
            })
        
        generate_license_agreement(license_obj)
        
        return Response({
            'message': 'License agreement generated',
            'license_id': str(license_obj.license_id),
            'file_url': license_obj.license_agreement_file.url if license_obj.license_agreement_file else None
        })
    @action(detail=True, methods=['post'], url_path='send-email')
    def send_email(self, request, pk=None):
        """
        Send license email to a specific contact.
        POST /licenses/{license_id}/send-email/
        
        Request body:
        {
            "email": "buyer@example.com"  # Optional - defaults to licensee's email
        }
        """
        license_obj = self.get_object()
        
        # Check if PDF exists
        if not license_obj.license_agreement_file:
            return Response(
                {'error': 'License agreement not generated yet. Call generate-agreement first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get email from request or fall back to licensee's email
        email = request.data.get('email')
        if not email:
            holding = license_obj.license_holdings.first()
            if holding:
                email = holding.licensee.music_professional.contact.email
            else:
                return Response(
                    {'error': 'No email provided and no licensee found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Build URLs and send
        license_url, track_url = build_download_urls(request, license_obj)
        send_license_email(license_obj, email, license_url, track_url)
        
        return Response({
            'message': 'License email sent',
            'license_id': str(license_obj.license_id),
            'sent_to': email
        })


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


# This endpoint is used to download the zip file that contains the track and license agreement- as opposed to the download_license_agreement and download_track endpoints that are used to download the license agreement and track separately/ no zip file
#They are save in LicenseDownload with a reference to license...that's what make them reachable
def download_assets(request, license_id, token):
    ld = get_object_or_404(LicenseDownload, license_id=license_id, token=token)
    if ld.expires_at <= timezone.now():
        raise Http404("Link expired")
    if not ld.zip_file or not default_storage.exists(ld.zip_file.name):
        raise Http404("Asset not found")

    # Preferred for DO Spaces/S3 (private objects):
    try:
        url = default_storage.url(ld.zip_file.name, expire=getattr(settings, "S3_PRESIGNED_TTL_SECONDS", 900))
        return redirect(url)
    except Exception:
        # Fallback for local storage or if presign fails
        name = os.path.basename(ld.zip_file.name)
        f = ld.zip_file.open("rb")
        return FileResponse(f, as_attachment=True, filename=name)