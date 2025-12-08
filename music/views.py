from django.shortcuts import render

# Create your views here.
from rest_framework import generics 
from .models import Track, Publisher, Contributor, Publishing, Contribution, Library, SocialMediaLink, MusicProfessional, FileFormat, TrackStorageFile
from .serializers import TrackSerializer, PublisherSerializer, ContributorSerializer, PublishingSerializer, ContributionSerializer, LibrarySerializer, SocialMediaLinkSerializer, MusicProfessionalSerializer, FileFormatSerializer, TrackStorageFileSerializer 
from rest_framework import viewsets 
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from .models import Track
from django.http import FileResponse
from django.urls import reverse

class TrackViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        print("DEBUG: TrackViewSet.list called")
        print(f"DEBUG: Request: {request.method} {request.path}")
        print(f"DEBUG: Query params: {request.query_params}")
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            print(f"ERROR in TrackViewSet.list: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


class PublisherViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        print("DEBUG: PublisherViewSet.list called")
        print(f"DEBUG: Request: {request.method} {request.path}")
        print(f"DEBUG: Query params: {request.query_params}")
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            print(f"ERROR in PublisherViewSet.list: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

class PublishingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Publishing.objects.all()
    serializer_class = PublishingSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        print("DEBUG: PublishingViewSet.list called")
        print(f"DEBUG: Request: {request.method} {request.path}")
        print(f"DEBUG: Query params: {request.query_params}")
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            print(f"ERROR in PublishingViewSet.list: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

class ContributorViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        print("DEBUG: ContributorViewSet.list called")
        print(f"DEBUG: Request: {request.method} {request.path}")
        print(f"DEBUG: Query params: {request.query_params}")
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            print(f"ERROR in ContributorViewSet.list: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
class ContributionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
    pagination_class = None
    
    def list(self, request, *args, **kwargs):
        print("DEBUG: ContributionViewSet.list called")
        print(f"DEBUG: Request: {request.method} {request.path}")
        print(f"DEBUG: Query params: {request.query_params}")
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            print(f"ERROR in ContributionViewSet.list: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

class LibraryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        print("DEBUG: LibraryViewSet.list called")
        print(f"DEBUG: Request: {request.method} {request.path}")
        print(f"DEBUG: Query params: {request.query_params}")
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            print(f"ERROR in LibraryViewSet.list: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

class SocialMediaLinkViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = SocialMediaLink.objects.all()
    serializer_class = SocialMediaLinkSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        print("DEBUG: SocialMediaLinkViewSet.list called")
        print(f"DEBUG: Request: {request.method} {request.path}")
        print(f"DEBUG: Query params: {request.query_params}")
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            print(f"ERROR in SocialMediaLinkViewSet.list: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

class MusicProfessionalViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = MusicProfessional.objects.all()
    serializer_class = MusicProfessionalSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        print("DEBUG: MusicProfessionalViewSet.list called")
        print(f"DEBUG: Request: {request.method} {request.path}")
        print(f"DEBUG: Query params: {request.query_params}")
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            print(f"ERROR in MusicProfessionalViewSet.list: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

class FileFormatViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = FileFormat.objects.all()
    serializer_class = FileFormatSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        print("DEBUG: FileFormatViewSet.list called")
        print(f"DEBUG: Request: {request.method} {request.path}")
        print(f"DEBUG: Query params: {request.query_params}")
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            print(f"ERROR in FileFormatViewSet.list: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

class TrackStorageFileViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = TrackStorageFile.objects.all()
    serializer_class = TrackStorageFileSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        print("DEBUG: TrackStorageFileViewSet.list called")
        print(f"DEBUG: Request: {request.method} {request.path}")
        print(f"DEBUG: Query params: {request.query_params}")
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            print(f"ERROR in TrackStorageFileViewSet.list: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
