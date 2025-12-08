from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from common.models import Contact


class CustomUser(AbstractUser):
    """Custom user model extending Django's AbstractUser."""
    # This is the central user model for your project.
    groups = models.ManyToManyField(
        Group,
        # ...
        related_name="custom_user_set" # We give it a unique name!
    )
    user_permissions = models.ManyToManyField(
        Permission,
        # ...
        related_name="custom_user_permissions_set" # And another unique name!
    )


class UserProfile(models.Model):
    """Model to store additional information for a user."""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    contact = models.OneToOneField( 
        Contact,
        on_delete=models.SET_NULL,  # if contact is deleted, set the user profile to null; dont delete the user profile
        related_name='user_profile',
        help_text="Contact information for the user.",
        null=True,
        blank=True
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile_and_contact(sender, instance, created, **kwargs):
    """
    Signal to create a UserProfile and a corresponding Contact
    automatically when a new user is created.
    """
    if created:
        # Use get_or_create to prevent race conditions or duplicate signals
        contact = Contact(
            email=instance.email,
            contact_type=Contact.ContactType.INDIVIDUAL,
        )
        contact.full_clean()  # Validate before saving
        contact.save()
        # Link the profile to the user and the contact
        UserProfile.objects.create(user=instance, contact=contact)