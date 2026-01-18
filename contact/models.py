from django.db import models
from django.utils import timezone
import uuid

class ContactSubmission(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    name = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    attachment = models.FileField(upload_to='contact_attachments/', blank=True, null=True)

    def __str__(self):
        return f"{self.email} - {self.created_at}" 