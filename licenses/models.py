from django.db import models
from django.core.exceptions import ValidationError
import uuid
from music.models import Track, Contributor, Contact, TrackStorageFile, MusicProfessional, ROLE_CHOICES
from transactions.models import OrderItem


# Create your models here.
class Copyright(models.Model):
    """A copyright of a track"""
    copyright_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                    help_text="Unique identifier for the copyright.")
    copyright_type = models.CharField(max_length=255, choices=[('Recording Copyright', 'Recording Copyright'), ('Composition Copyright', 'Composition Copyright')], null=False,
                                      help_text="The type of copyright (e.g., 'Recording Copyright', 'Composition Copyright').")
    description = models.TextField(blank=True, null=True,
                                   help_text="Additional notes or comments about the copyright.")
    copyright_date = models.DateField(blank=True, null=True,
                                          help_text="The date the copyright for the sound recording was established.")
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='copyrights',
                              help_text="The track to which the copyright applies.")
    note = models.TextField(blank=True, null=True,
                            help_text="Additional notes or comments about the copyright.")
    def __str__(self):
        return str(self.copyright_type) + " - " + str(self.track.title)

class CopyrightHolding(models.Model):
    """A copyright holding of a track as a join many to many relationship table between Copyright and MusicProfessional"""
    copyright_holding_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                    help_text="Unique identifier for the copyright holder.")
    copyright = models.ForeignKey(Copyright, on_delete=models.CASCADE, related_name='copyright_holdings',
                            help_text="The copyright record.")
    copyright_holder = models.ForeignKey(MusicProfessional, on_delete=models.CASCADE, related_name='copyright_holdings', blank=False, null=False,
                            help_text="The copyright holder.")
    copyright_holder_split = models.IntegerField(null=False,
                            help_text="The percentage of the copyright holder's share of the copyright.")
    copyright_holding_note = models.TextField(blank=True, null=True,
                            help_text="Additional notes or comments about the copyright holder.")
    def __str__(self):
        return str(self.copyright_holder) + " - " + str(self.copyright.copyright_id) + " - " + str(self.copyright_holder_split) + " - " + str(self.copyright.copyright_type)

class CopyrightStatus(models.Model):
    """A copyright status of a track"""
    copyright_status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                    help_text="Unique identifier for the copyright status.")
    copyright_status_option = models.CharField(max_length=255, choices=[('Active', 'Active'), ('Expired', 'Expired'), ('Cancelled', 'Cancelled')], null=False,
                            help_text="The type of copyright status (e.g., 'Active', 'Expired', 'Cancelled').")
    copyright_status_date = models.DateField(null=True, blank=True,
                            help_text="The date the copyright status was created.")
    copyright = models.ForeignKey(Copyright, on_delete=models.CASCADE, related_name='copyright_status',
                            help_text="The copyright record.")
    copyright_status_note = models.TextField(blank=True, null=True,
                            help_text="Additional notes or comments about the copyright status.")
    def __str__(self):
        return str(self.copyright_status_option) + " - " + str(self.copyright.copyright_id)    

class License_type(models.Model):
    """A license type of a track that will be used in the licenseOption with the TrackStorageFile"""
    license_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                    help_text="Unique identifier for the license type (e.g., 'Standard Sync License- mp3 and wav').")
    license_type_name = models.CharField(max_length=255, null=False,
                            help_text="The name of the license type.")
    license_template = models.TextField(null=False, blank=False, default=None,
                            help_text="The license template for the license type.")
    license_term = models.CharField(max_length=255, null=False,
                            help_text="Amount of years the license is valid for (e.g., '1 Year', '2 Years', unlimited').")
    transferability = models.CharField(max_length=255, choices=[('Transferable', 'Transferable'), ('Non-Transferable', 'Non-Transferable')],
                            help_text="The transferability of the license option (e.g., 'Transferable', 'Non-Transferable').")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False,
                            help_text="The price for the license option.")
    currency = models.CharField(max_length=255, null=False, default='USD',
                            help_text="The currency for the license option (e.g., 'USD', 'EUR', 'GBP').")
    download_limit = models.CharField(max_length=255, null=False,
                            help_text="The download limit for the license option (e.g., 'Unlimited', '100').")
    streaming_limit = models.CharField(max_length=255, null=False,
                            help_text="The streaming limit for the license option (e.g., 'Unlimited', '100').")
    monetized_radio_plays = models.CharField(max_length=255, null=False,
                            help_text="The monetized radio plays for the license option (e.g., 'Unlimited', '100').")
    video_rights = models.CharField(max_length=255, null=False,
                            help_text="The video rights for the license option.")
    royalty_payment = models.CharField(max_length=255, null=False,
                            help_text="The royalty payment for the license option.")
    credit_requirement = models.CharField(max_length=255, null=False, default='Yes',
                            help_text="The credit requirement for the license option.")

    def __str__(self):
        return str(self.license_type_name)

    # def clean(self):
    #     super().clean()
    #     if self.pk and self.tracks.count() == 0:
    #         raise ValidationError("A license must have at least one track.")
    
    # def __str__(self):
    #     track_titles = ", ".join([track.title for track in self.tracks.all()[:3]])
    #     return f"{self.license_id} - {track_titles}"

class Licensee(models.Model):
    '''
    A licensee who purchases a track license.
    '''
    licensee_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                    help_text="Unique identifier for the licensee.")
    music_professional = models.ForeignKey(MusicProfessional, on_delete=models.CASCADE, related_name='licensees', null=True, blank=True,
                            help_text="The licensee.")
    role = models.CharField(max_length=255, null=True, blank=True,
                            choices=ROLE_CHOICES,
                            help_text="The role of the licensee (e.g., 'Composer', 'Lyricist', 'Producer', Songwriter, Engineer, Singer, Performer ).")
    note = models.TextField(blank=True, null=True,
                            help_text="Additional notes or comments about the licensee.")
    def __str__(self):
        return str(self.licensee_id) + " - " + str(self.music_professional)
    
class TrackLicenseOptions(models.Model):
    """
    The reason I'm not adding the track as a foreingkey in track_storage_file is because a track_storage_files can be used by multiple tracks.
    one trackstoragefile can be used in multiple licenses
    """
    track_license_option_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                help_text="Unique identifier for the track license option.")
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='track_license_options')
    track_storage_file = models.ForeignKey(TrackStorageFile, on_delete=models.CASCADE, related_name='track_license_options')
    license_type = models.ForeignKey(License_type, on_delete=models.CASCADE, related_name='track_license_options')

    def __str__(self):
        return str(self.track_license_option_id) + " - " + str(self.track_storage_file) + " - " + str(self.license_type)

class License(models.Model):
    '''
    A license for a track generated when a license option is purchased.
    '''
    license_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                    help_text="Unique identifier for the license.")
    license_agreement_file = models.FileField(null=True, blank=True, upload_to='license_agreements',
                            help_text="The license agreement for the sound recording.")
    track_license_option = models.ForeignKey(TrackLicenseOptions, on_delete=models.CASCADE, related_name='licenses',
                                      help_text="The type of license (e.g., 'Wav, mp3, stems').")
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='licenses', null=True, blank=True,
                            help_text="The order item for the license.")
    created_date = models.DateTimeField(auto_now_add=True,
                            help_text="The date the license for the sound recording was established.")
    expiration_date = models.DateTimeField(null=True, blank=True,
                            help_text="The expiration date of the license for the sound recording.")
    license_email_sent_at = models.DateTimeField(null=True, blank=True,
                            help_text="The date and time the license email was sent.")
    license_note = models.TextField(blank=True, null=True,
                            help_text="Additional notes or comments about the license.")
    
    def __str__(self):
        return str(self.license_id) + " - " + str(self.track_license_option) + " - " + str(self.created_date)

class LicenseHolding(models.Model):
    '''
    A license holding as a many to many joining table between a license and a licensee.
    '''
    license_holding_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                    help_text="Unique identifier for the license holding.")
    license = models.ForeignKey(License, on_delete=models.CASCADE, related_name='license_holdings',
                            help_text="The license record.")
    licensee = models.ForeignKey(Licensee, on_delete=models.CASCADE, related_name='license_holdings',
                            help_text="The licensee.")
    licensee_split = models.IntegerField(null=True, blank=True,
                            help_text="The percentage of the licensee's share of the license.")
    license_holding_note = models.TextField(blank=True, null=True,
                            help_text="Additional notes or comments about the license holding.")
    def __str__(self):
        return str(self.license_holding_id) + " - " + str(self.license.license_id) + " - " + str(self.licensee) + " - " + str(self.licensee_split)

# License status
class LicenseStatus(models.Model):
    '''
    A license status.
    '''
    license_status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                    help_text="Unique identifier for the license status.")
    license_status_option = models.CharField(max_length=255, choices=[('Active', 'Active'), ('Expired', 'Expired'), ('Cancelled', 'Cancelled')],
                            help_text="The type of license status (e.g., 'Active', 'Expired', 'Cancelled').")
    license_status_date = models.DateTimeField(null=False, 
                            help_text="The date the license status was created.")
    license = models.ForeignKey(License, on_delete=models.CASCADE, related_name='license_status',
                            help_text="The license record.")
    license_status_note = models.TextField(blank=True, null=True,
                            help_text="Additional notes or comments about the license status.")
    def __str__(self):
        return str(self.license_status_id) + " - " + str(self.license_status_option) + " - " + str(self.license_status_date.strftime('%Y-%m-%d'))


    