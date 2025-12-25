from django.db import models
import uuid
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from common.models import Contact
from custom_users.models import CustomUser
from django.utils import timezone


class Track(models.Model):
    """
    Model representing a musical composition and its master recording.
    Contains all necessary metadata for internal management, digital distribution,
    and linking to legal contracts and audio file versions.
    """
    # Core Identification & Metadata
    track_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                               help_text="Unique identifier for the song.")
    artists_features_line = models.CharField(max_length=255, blank=True, null=True, default="GardlyRadicle",
                             help_text="The artists of the song formatted for posting.")        
    isrc_code = models.CharField(max_length=13, blank=True, null=True,
                           help_text="The ISRC code of the song.")      
    upc_code = models.CharField(max_length=12, blank=True, null=True,
                           help_text="The UPC code of the song.")    
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True,
                                  help_text="The thumbnail image of the song.")
    vinyl_thumbnail = models.ImageField(upload_to='vinyl_thumbnails/', blank=True, null=True,
                                        help_text="The vinyl thumbnail image of the song.") 
    cover_art = models.ImageField(upload_to='cover_arts/', blank=True, null=True,
                                  help_text="The cover art image of the song.")
    title = models.CharField(max_length=255,
                             help_text="The primary title of the song.")
    alternate_titles = models.JSONField(default=list, blank=True, null=True,
                                        help_text="Array of alternative titles, common misspellings, or working titles.")
    version_subtitle = models.CharField(max_length=255, blank=True, null=True,
                                        help_text="e.g., 'Instrumental,' 'Acoustic Mix,' 'Radio Edit,' 'Remix feat. [Artist]'.")
    description = models.TextField(blank=True, null=True,
                                   help_text="A brief overview or detailed description of the song.")
    # license_types = models.ManyToManyField('License_type', related_name='tracks', blank=True) #some tracks are not licensed
    release_date = models.DateField(default=timezone.now,
                                    help_text="The date the song was first commercially released.")
    language = models.CharField(max_length=10, default='en',
                                help_text="The primary language of the lyrics (if any), e.g., 'en', 'es'.")
    explicit_content = models.BooleanField(default=False,
                                           help_text="Flag indicating if the song contains explicit lyrics or themes.")
    lyrics = models.TextField(blank=True, null=True,
                              help_text="The lyrics of the song.")

    # Musical Characteristics
    bpm = models.IntegerField(blank=True, null=True, default=120,
                                    help_text="Beats Per Minute (BPM) of the song.")
    key = models.CharField(max_length=50, blank=True, null=True, default='C Major',
                           help_text="Musical key of the song (e.g., 'C Major', 'A Minor', 'F#m').")
    time_signature = models.CharField(max_length=10, blank=True, null=True, default='4/4',
                                      help_text="Time signature of the song (e.g., '4/4', '3/4').")
    duration_seconds = models.IntegerField(blank=True, null=True, default=120,
                                           help_text="Total duration of the song in seconds.")
    genres = models.JSONField(default=list, blank=True, null=True,
                              help_text="Array of primary and secondary genres (e.g., ['Hip-Hop', 'Trap']).")
    moods = models.JSONField(default=list, blank=True, null=True,
                             help_text="Array of moods or emotions evoked (e.g., ['Uplifting', 'Melancholy']).")
    keywords_tags = models.JSONField(default=list, blank=True, null=True,
                                     help_text="Additional keywords for search and categorization (e.g., ['summer', 'driving']).")
    instruments = models.JSONField(default=list, blank=True, null=True,
                                   help_text="List of prominent instruments in the track (e.g., ['piano', 'drums']).")
    vocal_description = models.CharField(max_length=100, blank=True, null=True,
                                         help_text="Describes the vocal presence (e.g., 'Male Lead', 'No Vocals').")
    # links
    buy_link = models.URLField(blank=True, null=True,
                               help_text="Link to purchase the track.")
    stream_link = models.URLField(blank=True, null=True,
                                  help_text="Link to stream the track.")
    download_link = models.URLField(blank=True, null=True,
                                    help_text="Link to download the track.")
    donation_link = models.URLField(blank=True, null=True,
                                    help_text="Link to donate to the creator. For example, donate to support making full song with the beat.")
    note = models.TextField(blank=True, null=True,
                            help_text="Additional notes or comments about the track.")
    
    def __str__(self):
        return str(self.track_id) + " - " + str(self.title)

class FileFormat(models.Model):
    """
    Represents an audio file format available for audio files.
    """
    FORMAT_CHOICES = [
        ('WAV', 'WAV'),
        ('MP3', 'MP3'),
        ('FLAC', 'FLAC'),
        ('Stems', 'Stems'),
        ('AIFF', 'AIFF'),
        ('OGG', 'OGG'),
        ('M4A', 'M4A'),
        ('ALAC', 'ALAC'),
        ('Sample', 'Sample'),
    ]
    # --- Core identifying fields ---
    name = models.CharField(max_length=20, choices=FORMAT_CHOICES, help_text="The display name of the format, e.g. 'WAV', 'MP3', 'FLAC', 'Stems', 'AIFF'")
    mime_type = models.CharField(max_length=50, help_text="MIME type used for HTTP responses, e.g. 'audio/wav' or 'audio/mpeg'.")
    extension = models.CharField(max_length=10, help_text="Typical file extension, e.g. '.wav', '.mp3', '.flac', '.stems', '.aiff', '.flac'.")

    # --- Technical details ---
    codec = models.CharField(max_length=50, blank=True, help_text="Codec or encoding standard, e.g. 'PCM 16-bit', 'MP3 (MPEG-1 Layer III)'.")
    compression = models.CharField(max_length=20, choices=[("lossless", "Lossless"), ("lossy", "Lossy"),], help_text="Indicates whether the format uses lossy or lossless compression.")
    bit_depth = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Bit depth (for uncompressed/lossless formats), e.g. 16 or 24.")
    sample_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Default or recommended sample rate in Hz (e.g. 44100, 48000).")

    # --- Business / system fields ---
    file_size_factor = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, help_text="Relative size factor vs WAV (e.g. MP3 = 0.15 means 15% of WAV size).")
    active = models.BooleanField(default=True, help_text="Whether this format is currently supported.")

    # --- Meta info ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "File Format"
        verbose_name_plural = "File Formats"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.extension})"


class TrackStorageFile(models.Model):
    """
    Represents an audio file and its path. Check TrackLicenseOptions for a joint table between Track and TrackStorageFile.
    """
    # includes samples, stems with vocals, mix
    track_storage_file_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                    help_text="Unique identifier for the track storage file.")
    description = models.CharField(max_length=255, blank=True, null=True,
                                  help_text="Description of the track storage file.")
    file_path = models.FileField(upload_to='track_storage_files',
                            help_text="The track storage file.")
    file_format = models.ForeignKey(FileFormat, on_delete=models.PROTECT, related_name='track_storage_files',
                                  help_text="The file format of the audio file from the file_format model.")
    bit_rate = models.IntegerField(blank=True, null=True,                 
                                  help_text="The bit rate of the audio file of the song (in kbps).")
    file_size = models.BigIntegerField(blank=True, null=True,
                                  help_text="The file size of the audio file of the song (in bytes).")
    created_at = models.DateTimeField(auto_now_add=True,
                                     help_text="The date the file was created/uploaded.")

    def __str__(self):
        return str(self.track_storage_file_id) + " - " + str(self.created_at)

class Library(models.Model):
    """
    Represents a collection of tracks for the website.
    """
    library_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                 help_text="Unique identifier for the library.")
    library_owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='library')
    library_name = models.CharField(max_length=255, null=False, blank=False, default='Library',
                                    help_text="The name of the library.")
    tracks = models.ManyToManyField(Track, related_name='libraries')
    note = models.TextField(blank=True, null=True,
                            help_text="Additional notes or comments about the library.")
    
    def __str__(self):
        return str(self.library_id) + " - " + str(self.library_name)

class MusicProfessional(models.Model):
    """A person/entity in the music industry who can contribute to or license tracks"""
    professional_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                       help_text="Unique identifier for the music professional.")
    contact = models.OneToOneField(Contact, on_delete=models.CASCADE, 
                                   related_name='music_professional',
                                   help_text="The contact information for the music professional.")
    
    # Shared professional info
    ref_code = models.CharField(max_length=13, blank=True, null=True,
                               help_text="ISNI or other reference code-if an artist")
    pro_affiliation = models.CharField(max_length=100, blank=True, null=True, help_text="The professional affiliation of the artist (e.g., 'ASCAP', 'BMI', 'SoundExchange').")
    ipi_number = models.CharField(max_length=20, blank=True, null=True, help_text="The IPI number of the artist.")
    note = models.TextField(blank=True, null=True, help_text="Additional notes or comments.")

# Make a table with role choices in the future if other producers are using the same template
ROLE_CHOICES = [('Composer', 'Composer'), ('Lyricist', 'Lyricist'), ('Producer', 'Producer'), ('Songwriter', 'Songwriter'), ('Engineer', 'Engineer'), ('Singer', 'Singer'), ('Performer', 'Performer'), ('Various', 'Various'), ('Other', 'Other')]

class Contributor(models.Model):
    """A person/entity who contributes to or create a track"""
    contributor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                 help_text="Unique identifier for the contributor.")
    music_professional = models.ForeignKey(MusicProfessional, on_delete=models.CASCADE,
                                          related_name='contributor')
    role = models.CharField(max_length=255,choices=ROLE_CHOICES,
                            help_text="The role of the contributor (e.g., 'Composer', 'Lyricist', 'Producer', Songwriter, Engineer, Singer, Performer ).")
    note = models.TextField(blank=True, null=True,
                            help_text="Additional notes or comments about the contributor.")
    def __str__(self):
        return str(self.contributor_id) + " " + self.role

class SocialMediaLink(models.Model):
    social_media_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                       help_text="Unique identifier for the social media link.")
    url = models.URLField()
    platform = models.CharField(max_length=50, blank=True, null=True)  # 'Instagram', 'Twitter', etc.
    music_professional = models.ForeignKey(MusicProfessional, on_delete=models.CASCADE, related_name='social_media_links')
    def __str__(self):
        return str(self.social_media_id) + " " + self.platform

# Many to many relationship between Contributor and Track
class Contribution(models.Model):
    CONTRIBUTION_TYPE_CHOICES = [
        ('Creative', 'Creative'),
        ('Technical', 'Technical'),
        ('Administrative', 'Administrative'),
        ('Various', 'Various'),
    ]
    """A contribution to a track as a joining table for many to many relationship between Contributor and Track"""
    contribution_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                        help_text="Unique identifier for the contribution.")
    contribution_type = models.CharField(max_length=255, choices=CONTRIBUTION_TYPE_CHOICES, null=False, blank=False,
                                        help_text="The type of contribution (e.g., 'composer', 'performer', 'engineer').")
    contribution_description = models.TextField(blank=True, null=True,
                                            help_text="Getting more specific about the contribution/input.")
    contribution_date = models.DateField(blank=True, null=True,
                                        help_text="The date the contribution was made.")
    contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE, related_name='contributions',
                                    help_text="The contributor who made the contribution.")
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='contributions',
                            help_text="The track that was contributed to.")     
    contribution_note = models.TextField(blank=True, null=True,
                                        help_text="Additional notes or comments about the contribution.")
    def __str__(self):
        return str(self.contribution_id) + " " + str(self.track.title)

class Publisher(models.Model):
    """A publisher of a track"""
    publisher_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                    help_text="Unique identifier for the publisher.")
    website = models.URLField(blank=True, null=True, help_text="Official website of the publisher.")

    pro_affiliation = models.CharField(max_length=100, blank=True, null=True,
                                       help_text="The publisher's PRO (e.g., 'ASCAP', 'BMI').")

    # This allows you to do publisher.contact.addresses.all()
    contact = models.OneToOneField(Contact, on_delete=models.CASCADE, related_name='publisher')

    note = models.TextField(blank=True, null=True,
                            help_text="Additional notes or comments about the publisher.")

    def __str__(self):
        return str(self.publisher_id) + " " + str(self.contact.first_name) + " " + str(self.contact.last_name)

class Publishing(models.Model):
    """A publishing of a track as a joining table for many to many relationship between Track and Publisher"""
    publishing_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                    help_text="Unique identifier for the publishing.")
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='publishings')
    publishing_date = models.DateField(blank=True, null=True,
                                    help_text="The date the publishing was published.")
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='publishings')
    note = models.TextField(blank=True, null=True,
                            help_text="Additional notes or comments about the publishing.")
    def __str__(self):  
        return str(self.publishing_id) + " " + str(self.track.title) + " " + str(self.publishing_date.strftime('%Y-%m-%d'))


# # --- Main Song Model ---
# isrc code for sound recording
#UPC code for releaase
#ISWC code for composition
#ISNI code for artist
# Title - The official name of a song or album.
# Artist Name - The name of the primary performer(s) of the song or album.
# Release Date - The scheduled date when the song or album will be made available to the public.
# Songwriter(s) - Individuals who composed the music and wrote the lyrics of the song.
# Producer(s) - Individuals responsible for overseeing the recording and production of the track.
# Musicians - Performers who played instruments or contributed vocals to the track.
# ISRC (International Standard Recording Code) - A unique code assigned to each individual recording for
# the purpose of tracking and royalty payments.
# UPC (Universal Product Code) / Barcode - A unique code assigned to an album or single, used in retail
# and digital distribution to track sales and inventory.
# Copyright Information - Legal information that identifies the owner(s) of the song and the year the
# copyright was established.
# Publishing Information - Details about the music publishers who manage the rights and royalties for the
# songwriters’ compositions.
# Mechanical Rights - Rights that allow for the reproduction of the music in physical or digital formats.
# Genre - A category that describes the style of the music (e.g., pop, rock, hip-hop).
# Mood/Theme - Descriptive terms that capture the emotional or thematic essence of the music (e.g., happy,
# sad, inspirational).
# Language - The primary language(s) in which the song’s lyrics are performed.
# Lyrics - The complete text of the song’s words.
# BPM (Beats Per Minute) - The tempo of the song, indicating how many beats occur in one minute.
# Key - The musical scale in which the song is composed (e.g., C major, A minor).
# Duration - The total length of the song, measured in minutes and seconds.
# Audio Quality - Technical specifications of the audio file, including bit rate, sample rate, and format, which
# affect the sound quality.
# Cover Art - The visual image associated with the album or single, used for marketing and branding.
# Release Notes - Additional information or commentary about the release, often included in press materials.
# artist = models.CharField(max_length=255, null=False, help_text="The artist of the song.")  
