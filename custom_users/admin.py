from django.contrib import admin
from .models import CustomUser  # Import the CustomUser model           
from django.contrib.auth.admin import UserAdmin
# Register your models here.
class CustomUserAdmin(UserAdmin):
    # ... your custom admin configurations (list_display, fieldsets, etc.) ...
    pass
admin.site.register(CustomUser, CustomUserAdmin)

