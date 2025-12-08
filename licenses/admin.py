from django.contrib import admin
from .models import Copyright, CopyrightHolding, CopyrightStatus, License, LicenseHolding, LicenseStatus, License_type, Licensee, TrackLicenseOptions

# Register your models here.
admin.site.register(Copyright)
admin.site.register(CopyrightHolding)
admin.site.register(CopyrightStatus)
admin.site.register(License)
admin.site.register(LicenseHolding)
admin.site.register(LicenseStatus)
admin.site.register(License_type)
admin.site.register(Licensee)
admin.site.register(TrackLicenseOptions)