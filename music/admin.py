from django.contrib import admin
from .models import Track, Publisher, Contributor, Publishing, Contribution, Library, FileFormat, SocialMediaLink, MusicProfessional, TrackStorageFile
# Register your models here.

admin.site.register(FileFormat)
admin.site.register(Track)
admin.site.register(Publisher)
admin.site.register(Contributor)    
admin.site.register(Publishing)
admin.site.register(Contribution)
admin.site.register(Library)
admin.site.register(SocialMediaLink)
admin.site.register(MusicProfessional)
admin.site.register(TrackStorageFile)


