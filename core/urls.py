from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('summernote/', include('django_summernote.urls')), # Added summernote URLs
    path('api/v1/', include('music.urls')),
    path('api/v1/', include('transactions.urls')),
    path('api/v1/', include('licenses.urls')),
    path('api/v1/', include('common.urls')),
    path('api/v1/', include('custom_users.urls')),
    path('api/v1/', include('newsletter.urls')),
    
]

# ONLY during development, serve media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)