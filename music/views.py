from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import Track
from .serializers import TrackSerializer
from rest_framework import viewsets 
from rest_framework import permissions

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
# class LibraryViewSet(viewsets.ModelViewSet):
#     queryset = Library.objects.all()
#     serializer_class = LibrarySerializer

# class TrackViewSet(generics.ListCreateAPIView):
#     queryset = Track.objects.all()
#     serializer_class = TrackSerializer

# class TrackDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Track.objects.all()
#     serializer_class = TrackSerializer

# class LibraryViewSet(generics.ListCreateAPIView):
#     queryset = Library.objects.all()
#     serializer_class = LibrarySerializer  

# class LibraryDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Library.objects.all()
#     serializer_class = LibrarySerializer

# track_id
# audio_file
# artist
# thumbnail
# vinyl_thumbnail
# title
# alternate_titles
# version_subtitle
# description
# release_date
# creation_date
# language
# explicit_content
# # Musical Characteristics
# tempo_bpm
# key
# time_signature
# duration_seconds
# genres
# moods
# keywords_tags
# instruments
# vocal_description
