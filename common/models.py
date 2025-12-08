from django.db import models
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
# Create your models here.

class Contact(models.Model):
    '''
    Contact for a user or musicprofessional.
    '''
    class ContactType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', 'Individual'
        COMPANY = 'COMPANY', 'Company'

    contact_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact_type = models.CharField(max_length=10, choices=ContactType.choices, default=ContactType.INDIVIDUAL)

    # Fields for an individual
    first_name = models.CharField(max_length=255, blank=True, help_text="The first name of the contact.")
    last_name = models.CharField(max_length=255, blank=True, help_text="The last name of the contact.")
    sudo_name = models.CharField(max_length=255, blank=True, help_text="The artist name, alias, or stage name of the contact.")
    
    # Field for a company or organization name
    company_name = models.CharField(max_length=255, blank=True, help_text="The name of the company or organization.")
    registration_number = models.CharField(max_length=255, blank=True, help_text="The registration number of the company or organization.")
    

    email = models.EmailField(blank=False)
    phone_number = models.CharField(max_length=20, blank=True)

    def clean(self):  # ← Add here, inside the class
        """Custom validation: company_name required if contact_type is COMPANY"""
        super().clean()
        if self.contact_type == self.ContactType.COMPANY and not self.company_name:
            raise ValidationError({
                'company_name': 'Company name is required when contact type is Company.'
            })

    def __str__(self):
        if self.contact_type == self.ContactType.INDIVIDUAL:
            return f"{self.first_name} {self.last_name} {self.sudo_name}".strip()
        return self.company_name


class Address(models.Model):
    '''
    Address for a contact.
    '''
    class AddressType(models.TextChoices):
        BILLING = 'BILLING', 'Billing'
        SHIPPING = 'SHIPPING', 'Shipping'
        MAILING = 'MAILING', 'Mailing'
        REGISTRATION = 'REGISTRATION', 'Registration'

    address_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=15, choices=AddressType.choices, default=AddressType.MAILING)

    address_line_1 = models.CharField(max_length=255, null=False, blank=False)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, null=False, blank=False)
    state_province = models.CharField(max_length=100, help_text="State or Province")
    postal_code = models.CharField(max_length=20, null=False, blank=False)
    country = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return f"{self.address_line_1}, {self.city}"
    