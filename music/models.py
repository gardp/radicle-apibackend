from django.db import models
import uuid
from django.contrib.postgres.fields import JSONField

# # Create your models here.
# class ContractTemplate(models.Model):
#     """
#     Placeholder for the ContractTemplate model.
#     This model would define different types of licensing contracts,
#     their terms, pricing tiers, and royalty splits.
#     """
#     contract_template_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=255, unique=True, help_text="Name of the contract template (e.g., 'Standard Sync License')")
#     description = models.TextField(blank=True, null=True)
#     license_type = models.CharField(max_length=100, help_text="Type of license (e.g., 'Synchronization', 'Mechanical')")
#     terms_text = models.TextField(blank=True, null=True, help_text="Full legal text of the contract template.")
#     # JSONField to store flexible pricing tiers (e.g., {'basic': 50, 'premium': 150})
#     price_tiers = models.JSONField(default=dict, blank=True, null=True)
#     royalty_percentage_master = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,
#                                                     help_text="Default master royalty percentage for you as owner (e.g., 0.50 for 50%)")
#     royalty_percentage_publishing = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,
#                                                        help_text="Default publishing royalty percentage for you as owner")
#     exclusive = models.BooleanField(default=False, help_text="Does this template grant exclusive rights?")
#     territory_restriction = models.CharField(max_length=255, blank=True, null=True,
#                                             help_text="e.g., 'Worldwide', 'North America'")
#     term_length_years = models.IntegerField(blank=True, null=True, help_text="Duration of the license in years")

#     def __str__(self):
#         return self.name
    
# class CopyRight(models.Model):
#     copyright_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
#                                    help_text="Unique identifier for the copyright.")
#     copyright_year = models.IntegerField(blank=True, null=True,
#                                          help_text="The year the copyright for the sound recording was established.")
#     copyright_holder_master = models.CharField(max_length=255, blank=True, null=True,
#                                                help_text="The legal entity or individual holding the copyright for the master recording (e.g., your name/company name).")
#     copyright_holder_composition = models.CharField(max_length=255, blank=True, null=True,
#                                                     help_text="The legal entity or individual holding the copyright for the musical composition (e.g., your name/publishing company).")    
#     song_copyright = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='copyrights')
    
#     def __str__(self):
#         return f"{self.song.title} - Copyright {self.copyright_year}"
    
#     class Meta:
#         verbose_name = "Copyright"
#         verbose_name_plural = "Copyrights"
#         ordering = ['song__title', 'copyright_year']


# class Contributor(models.Model):
#     """
#     Placeholder for the Contributor model.
#     To track other individuals involved in the music (e.g., engineers, featured artists).
#     """
#     contributor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=255, null=False)
#     email = models.EmailField(blank=True, null=True)
#     pro_affiliation = models.CharField(max_length=100, blank=True, null=True,
#                                        help_text="e.g., 'ASCAP', 'BMI', 'SoundExchange'")
#     ipi_cae_number = models.CharField(max_length=20, blank=True, null=True)

#     def __str__(self):
#         return self.name

# # --- Main Song Model ---

class Track(models.Model):
    """
    Model representing a musical composition and its master recording.
    Contains all necessary metadata for internal management, digital distribution,
    and linking to legal contracts.
    """
    # Core Identification & Metadata
    track_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                               help_text="Unique identifier for the song.")
    audio_file = models.FileField(upload_to='tracks/', blank=True, null=True, max_length=255,
                                  help_text="The audio file of the song.")
    artist = models.CharField(max_length=255, null=False,
                                help_text="The artist of the song.")                              
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True,
                                  help_text="The thumbnail image of the song.")
    vinyl_thumbnail = models.ImageField(upload_to='vinyl_thumbnails/', blank=True, null=True,
                                        help_text="The vinyl thumbnail image of the song.") 
    title = models.CharField(max_length=255, null=False,
                             help_text="The primary title of the song.")
    alternate_titles = models.JSONField(default=list, blank=True, null=True,
                                        help_text="Array of alternative titles, common misspellings, or working titles.")
    version_subtitle = models.CharField(max_length=255, blank=True, null=True,
                                        help_text="e.g., 'Instrumental,' 'Acoustic Mix,' 'Radio Edit,' 'Remix feat. [Artist]'.")
    description = models.TextField(blank=True, null=True,
                                   help_text="A brief overview or detailed description of the song.")
    release_date = models.DateField(blank=True, null=True,
                                    help_text="The date the song was first commercially released.")
    creation_date = models.DateField(blank=True, null=True,
                                     help_text="The date the song was composed/first created.")
    language = models.CharField(max_length=10, default='en',
                                help_text="The primary language of the lyrics (if any), e.g., 'en', 'es'.")
    explicit_content = models.BooleanField(default=False,
                                           help_text="Flag indicating if the song contains explicit lyrics or themes.")
    # Musical Characteristics
    tempo_bpm = models.IntegerField(blank=True, null=True,
                                    help_text="Beats Per Minute (BPM) of the song.")
    key = models.CharField(max_length=50, blank=True, null=True,
                           help_text="Musical key of the song (e.g., 'C Major', 'A Minor', 'F#m').")
    time_signature = models.CharField(max_length=10, blank=True, null=True,
                                      help_text="Time signature of the song (e.g., '4/4', '3/4').")
    duration_seconds = models.IntegerField(null=True,
                                           help_text="Total duration of the song in seconds.")
    genres = models.JSONField(default=list, null=True,
                              help_text="Array of primary and secondary genres (e.g., ['Hip-Hop', 'Trap']).")
    moods = models.JSONField(default=list, blank=True, null=True,
                             help_text="Array of moods or emotions evoked (e.g., ['Uplifting', 'Melancholy']).")
    keywords_tags = models.JSONField(default=list, blank=True, null=True,
                                     help_text="Additional keywords for search and categorization (e.g., ['summer', 'driving']).")
    instruments = models.JSONField(default=list, blank=True, null=True,
                                   help_text="List of prominent instruments in the track (e.g., ['piano', 'drums']).")
    vocal_description = models.CharField(max_length=100, blank=True, null=True,
                                         help_text="Describes the vocal presence (e.g., 'Male Lead', 'No Vocals').")

#     # Audio File References & Previews
#     audio_file_preview_url = models.URLField(max_length=500, blank=True, null=True,
#                                              help_text="URL to a watermarked or low-quality preview MP3.")
#     audio_file_preview_watermarked = models.BooleanField(default=True,
#                                                           help_text="Indicates if the preview is watermarked.")
#     cover_art_thumbnail_url = models.URLField(max_length=500, blank=True, null=True,
#                                                 help_text="URL to the small cover art image (e.g., 128x128px).")
#     cover_art_icon_url = models.URLField(max_length=500, blank=True, null=True,
#                                          help_text="URL to a very small icon version of the cover art.")
#     cover_art_medium_url = models.URLField(max_length=500, blank=True, null=True,
#                                             help_text="URL to a medium resolution cover art image (e.g., 600x600px).")
#     cover_art_large_url = models.URLField(max_length=500, blank=True, null=True,
#                                            help_text="URL to the high-resolution cover art image (e.g., 3000x3000px).")

#     # Digital Distribution Identifiers & Links
#     isrc = models.CharField(max_length=12, unique=True, blank=True, null=True,
#                             help_text="International Standard Recording Code for the specific master recording.")
#     iswc = models.CharField(max_length=11, unique=True, blank=True, null=True,
#                             help_text="International Standard Musical Workcode for the underlying musical composition.")
#     upc_ean = models.CharField(max_length=14, blank=True, null=True,
#                                help_text="Universal Product Code / European Article Number for the overall release (if applicable).")
#     spotify_link = models.URLField(max_length=500, blank=True, null=True)
#     apple_music_link = models.URLField(max_length=500, blank=True, null=True)
#     youtube_link = models.URLField(max_length=500, blank=True, null=True)
#     soundcloud_link = models.URLField(max_length=500, blank=True, null=True)
#     distributor_internal_id = models.CharField(max_length=255, blank=True, null=True,
#                                                help_text="Any ID assigned by your digital distributor.")

#     # Rights Holder & Contributor Information (Core)
#     primary_artist_name = models.CharField(max_length=255, null=False,
#                                            help_text="The main performing artist name (your artist name).")
#     producer_name = models.CharField(max_length=255, blank=True, null=True,
#                                      help_text="Name of the producer(s) (likely yourself).")
#     lyricist_composer_name = models.CharField(max_length=255, blank=True, null=True,
#                                               help_text="The primary lyricist/composer name (likely yourself).")
#     pro_affiliation_master = models.CharField(max_length=100, blank=True, null=True,
#                                               help_text="Performance Rights Org for Master Rights (e.g., 'SoundExchange').")
#     pro_affiliation_composition = models.CharField(max_length=100, blank=True, null=True,
#                                                    help_text="Performance Rights Org for Composition Rights (e.g., 'ASCAP', 'BMI').")

#     # Administrative & Internal
#     internal_notes = models.TextField(blank=True, null=True)
#     is_available_for_purchase = models.BooleanField(default=True,
#                                                     help_text="Flag to quickly enable/disable song availability on your site.")
#     upload_timestamp = models.DateTimeField(auto_now_add=True,
#                                             help_text="When the song record was created/uploaded to your system.")
#     last_updated_timestamp = models.DateTimeField(auto_now=True,
#                                                   help_text="When the song record was last modified.")
#     # Relationships (Foreign Keys)
#     default_license_contract_template = models.ForeignKey(
#         ContractTemplate,
#         on_delete=models.SET_NULL,  # Or models.PROTECT, depending on your desired behavior
#         null=True, blank=True,
#         related_name='default_songs',
#         help_text="Links to a default contract template that applies to this song for initial licensing."
#     )

#     class Meta:
#         verbose_name = "Song"
#         verbose_name_plural = "Songs"
#         ordering = ['title', 'release_date']

#     def __str__(self):
#         return f"{self.title} by {self.primary_artist_name}"

# # --- M2M for SongContributors (Junction Table) ---
# # This is a good practice to explicitly define the intermediate model
# # when you need extra fields on the relationship (like 'role' or 'contribution_percentage').

# class SongContributor(models.Model):
#     """
#     Junction table to link Songs to Contributors with specific roles and percentages.
#     """
#     song = models.ForeignKey(Song, on_delete=models.CASCADE)
#     contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE)
#     role = models.CharField(max_length=100, null=False,
#                             help_text="e.g., 'Featured Artist', 'Mixing Engineer', 'Co-Writer'")
#     contribution_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,
#                                                   help_text="Optional: Share of ownership (e.g., 0.1 for 10%).")

#     class Meta:
#         unique_together = ('song', 'contributor', 'role') # A contributor can have one role per song
#         verbose_name = "Song Contributor"
#         verbose_name_plural = "Song Contributors"

#     def __str__(self):
#         return f"{self.song.title} - {self.contributor.name} ({self.role})"

