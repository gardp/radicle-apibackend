from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta
from django.core.files import File
import os

from common.models import Contact, Address
from custom_users.models import UserProfile
from music.models import (
    Track, FileFormat, TrackStorageFile, MusicProfessional, 
    Contributor, Contribution, Publisher, Publishing, Library
)
from licenses.models import (
    License_type, Copyright, CopyrightHolding, CopyrightStatus,
    Licensee, TrackLicenseOptions, License, LicenseHolding, LicenseStatus
)
from transactions.models import Buyer, Order, OrderItem, Payment, Receipt

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with initial development data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        self.create_users()
        self.create_file_formats()
        self.create_music_professionals()
        self.create_tracks()
        self.create_libraries()
        self.create_license_types()
        self.create_track_license_options()
        # self.create_buyers()
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def create_users(self):
        """Create test users with profiles"""
        self.stdout.write('  Creating users...')
        
        # Admin user (profile created via signal)
        admin, created = User.objects.get_or_create(
            username='admin_user',
            defaults={
                'email': 'gardly.philoctete@gmail.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('8891YldRaGPHIL')
            admin.save()
        
        # Regular test user
        self.test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            self.test_user.set_password('test123')
            self.test_user.save()

    def create_file_formats(self):
        """Create audio file formats"""
        self.stdout.write('  Creating file formats...')
        
        formats = [
            {'name': 'WAV', 'mime_type': 'audio/wav', 'extension': '.wav', 
             'codec': 'PCM 16-bit', 'compression': 'lossless', 'bit_depth': 16, 'sample_rate': 44100},
            {'name': 'MP3', 'mime_type': 'audio/mpeg', 'extension': '.mp3', 
             'codec': 'MP3', 'compression': 'lossy', 'file_size_factor': Decimal('0.15')},
            {'name': 'FLAC', 'mime_type': 'audio/flac', 'extension': '.flac', 
             'codec': 'FLAC', 'compression': 'lossless', 'bit_depth': 24, 'sample_rate': 48000},
            {'name': 'Stems', 'mime_type': 'application/zip', 'extension': '.zip', 
             'codec': 'Various', 'compression': 'lossless'},
        ]
        
        for fmt in formats:
            FileFormat.objects.get_or_create(name=fmt['name'], defaults=fmt)
        
        self.wav_format = FileFormat.objects.get(name='WAV')
        self.mp3_format = FileFormat.objects.get(name='MP3')

    def create_music_professionals(self):
        """Create music professionals (artists, producers)"""
        self.stdout.write('  Creating music professionals...')
        
        # Main artist contact
        self.artist_contact, _ = Contact.objects.get_or_create(
            email='gardly.philoctete@gmail.com',
            defaults={
                'first_name': 'Gardly',
                'last_name': 'Radicle',
                'sudo_name': 'GardlyRadicle',
                'contact_type': Contact.ContactType.INDIVIDUAL,
            }
        )
        
        # Add address
        Address.objects.get_or_create(
            contact=self.artist_contact,
            address_type=Address.AddressType.MAILING,
            defaults={
                'address_line_1': '123 Music Lane',
                'city': 'Los Angeles',
                'state_province': 'CA',
                'postal_code': '90001',
                'country': 'USA',
            }
        )
        
        # Music professional
        self.artist, _ = MusicProfessional.objects.get_or_create(
            contact=self.artist_contact,
            defaults={
                'pro_affiliation': 'ASCAP',
            }
        )
        
        # Contributor
        self.contributor, _ = Contributor.objects.get_or_create(
            music_professional=self.artist,
            role='Producer',
        )

    def create_tracks(self):
        """Create sample tracks"""
        self.stdout.write('  Creating tracks...')
        
        tracks_data = [
            {
                'title': 'Summer Vibes',
                'bpm': 120,
                'key': 'C Major',
                'genres': ['Hip-Hop', 'Trap'],
                'moods': ['Uplifting', 'Energetic'],
                'duration_seconds': 180,
                'file_path': '/host_music/Logic/Whisper/Lust2Luv Mastered 20240521.wav', # explicit path for docker 
                'artists_features_line': 'GardlyRadicle',
                'thumbnail': '/host_media/logo avatar-web-promo- images/babypic_cartoon.png',  # explicit path
                'vinyl_thumbnail': '/host_media/logo avatar-web-promo- images/vinyl-red.png',  # explicit path
                'cover_art': '/host_media/logo avatar-web-promo- images/ChatGPT Image Apr 24, 2025, 12_02_08 AM.png',  # explicit path
                'buy_link': 'https://youtube.com/buy',
                'stream_link': 'https://youtube.com/stream',
                'download_link': 'https://youtube.com/download',
                'donation_link': 'https://youtube.com/donate',

            },
            {
                'title': 'Midnight Dreams',
                'bpm': 85,
                'key': 'A Minor',
                'genres': ['R&B', 'Soul'],
                'moods': ['Melancholy', 'Smooth'],
                'duration_seconds': 210,
                'file_path': '/host_music/Logic/Samba Rele/Gardly Asimilak Test/Gardly_Asimilak_ Mastered 20240424.wav',  # explicit path for docker 
                'artists_features_line': 'GardlyRadicle',
                'thumbnail': '/host_media/logo avatar-web-promo- images/babypic_cartoon.png',  # explicit path
                'vinyl_thumbnail': '/host_media/logo avatar-web-promo- images/vinyl-red.png',  # explicit path
                'cover_art': '/host_media/logo avatar-web-promo- images/ChatGPT Image Apr 24, 2025, 12_02_08 AM.png',  # explicit path
                'buy_link': 'https://example.com/buy',
                'stream_link': 'https://example.com/stream',
                'download_link': 'https://example.com/download',
                'donation_link': 'https://example.com/donate',
            },
            {
                'title': 'City Lights',
                'bpm': 140,
                'key': 'F Major',
                'genres': ['Electronic', 'Pop'],
                'moods': ['Driving', 'Atmospheric'],
                'duration_seconds': 195,
                'file_path': '/host_music/Music/Media.localized/Music/Rita Ora & Imanbek/Bang - EP/01 Big (feat. Gunna).m4a',  # explicit path for docker 
                'artists_features_line': 'GardlyRadicle',
                'thumbnail': '/host_media/logo avatar-web-promo- images/babypic_cartoon.png',  # explicit path
                'vinyl_thumbnail': '/host_media/logo avatar-web-promo- images/vinyl-red.png',  # explicit path
                'cover_art': '/host_media/logo avatar-web-promo- images/ChatGPT Image Apr 24, 2025, 12_02_08 AM.png',  # explicit path
                'buy_link': 'https://youtube.com/buy',
                'stream_link': 'https://youtube.com/stream',
                'download_link': 'https://youtube.com/download',
                'donation_link': 'https://youtube.com/donate',
            },
            {
                'title': 'Summer Vibes',
                'bpm': 120,
                'key': 'C Major',
                'genres': ['Hip-Hop', 'Trap'],
                'moods': ['Uplifting', 'Energetic'],
                'duration_seconds': 180,
                'file_path': '/host_music/Logic/Whisper/Lust2Luv Mastered 20240521.wav',  # explicit path for docker 
                'artists_features_line': 'GardlyRadicle',
                'thumbnail': '/host_media/logo avatar-web-promo- images/babypic_cartoon.png',  # explicit path
                'vinyl_thumbnail': '/host_media/logo avatar-web-promo- images/vinyl-red.png',  # explicit path
                'cover_art': '/host_media/logo avatar-web-promo- images/ChatGPT Image Apr 24, 2025, 12_02_08 AM.png',  # explicit path
                'buy_link': 'https://youtube.com/buy',
                'stream_link': 'https://youtube.com/stream',
                'download_link': 'https://youtube.com/download',
                'donation_link': 'https://youtube.com/donate',
            },
            {
                'title': 'Midnight Dreams',
                'bpm': 85,
                'key': 'A Minor',
                'genres': ['R&B', 'Soul'],
                'moods': ['Melancholy', 'Smooth'],
                'duration_seconds': 210,
                'file_path': '/host_music/Logic/Samba Rele/Gardly Asimilak Test/Gardly_Asimilak_ Mastered 20240424.wav',  # explicit path for docker 
                'artists_features_line': 'GardlyRadicle',
                'thumbnail': '/host_media/logo avatar-web-promo- images/babypic_cartoon.png',  # explicit path
                'vinyl_thumbnail': '/host_media/logo avatar-web-promo- images/vinyl-red.png',  # explicit path
                'cover_art': '/host_media/logo avatar-web-promo- images/ChatGPT Image Apr 24, 2025, 12_02_08 AM.png',  # explicit path
                'buy_link': 'https://youtube.com/buy',
                'stream_link': 'https://youtube.com/stream',
                'download_link': 'https://youtube.com/download',
                'donation_link': 'https://youtube.com/donate',
            },
            {
                'title': 'City Lights',
                'bpm': 140,
                'key': 'F Major',
                'genres': ['Electronic', 'Pop'],
                'moods': ['Driving', 'Atmospheric'],
                'duration_seconds': 195,
                'file_path': '/host_music/Music/Media.localized/Music/Rita Ora & Imanbek/Bang - EP/01 Big (feat. Gunna).m4a',  # explicit path for docker 
                'artists_features_line': 'GardlyRadicle',
                'thumbnail': '/host_media/logo avatar-web-promo- images/babypic_cartoon.png',  # explicit path
                'vinyl_thumbnail': '/host_media/logo avatar-web-promo- images/vinyl-red.png',  # explicit path
                'cover_art': '/host_media/logo avatar-web-promo- images/ChatGPT Image Apr 24, 2025, 12_02_08 AM.png',  # explicit path
                'buy_link': 'https://youtube.com/buy',
                'stream_link': 'https://youtube.com/stream',
                'download_link': 'https://youtube.com/download',
                'donation_link': 'https://youtube.com/donate',
            },
        ]
        
        self.tracks = []
        for data in tracks_data:
            # Pop file_path before creating Track (it's not a Track field)
            file_path = data.pop('file_path')
            thumbnail = data.pop('thumbnail')
            vinyl_thumbnail = data.pop('vinyl_thumbnail')
            cover_art = data.pop('cover_art')
            track, _ = Track.objects.update_or_create(
                title=data['title'],
                defaults=data
            )
            # Store file_path on track object for later use
            track._file_path = file_path
            track._thumbnail = thumbnail
            track._vinyl_thumbnail = vinyl_thumbnail
            track._cover_art = cover_art
            self.tracks.append(track)
            
            with open(track._thumbnail, 'rb') as f:
                track.thumbnail.save(os.path.basename(track._thumbnail), File(f))
            with open(track._vinyl_thumbnail, 'rb') as f:
                track.vinyl_thumbnail.save(os.path.basename(track._vinyl_thumbnail), File(f))
            with open(track._cover_art, 'rb') as f:
                track.cover_art.save(os.path.basename(track._cover_art), File(f))
            


            # Add contribution
            Contribution.objects.get_or_create(
                contributor=self.contributor,
                track=track,
                defaults={
                    'contribution_type': 'Creative',
                    'contribution_date': date.today(),
                }
            )
            
            # Add copyright
            copyright, _ = Copyright.objects.get_or_create(
                track=track,
                copyright_type='Recording Copyright',
                defaults={'copyright_date': date.today()}
            )
            
            CopyrightHolding.objects.get_or_create(
                copyright=copyright,
                copyright_holder=self.artist,
                defaults={'copyright_holder_split': 100}
            )

    def create_libraries(self):
        """Create libraries and assign all tracks to each"""
        self.stdout.write('  Creating libraries...')
    
        # pick an owner for the libraries
        owner = User.objects.get(username='admin_user')  # or self.test_user
    
        library_names = [
            'Featured Library',
            'Beat Store Library',
            'All Tracks Library',
        ]
    
        self.libraries = []
        for name in library_names:
            library, _ = Library.objects.get_or_create(
                library_owner=owner,
                library_name=name,
            )
            library.tracks.add(*self.tracks)
            self.libraries.append(library)
            
    def create_license_types(self):
        """Create license types"""
        self.stdout.write('  Creating license types...')
        
        license_types = [
            {
                'license_type_name': 'Basic License',
                'license_template': 'Basic license agreement template...',
                'license_term': '1 Year',
                'transferability': 'Non-Transferable',
                'price': Decimal('29.99'),
                'download_limit': '1',
                'streaming_limit': '10000',
                'monetized_radio_plays': '0',
                'video_rights': 'Non-Monetized Only',
                'royalty_payment': 'None',
            },
            {
                'license_type_name': 'Premium License',
                'license_template': 'Premium license agreement template...',
                'license_term': '2 Years',
                'transferability': 'Non-Transferable',
                'price': Decimal('99.99'),
                'download_limit': '3',
                'streaming_limit': '100000',
                'monetized_radio_plays': '1000',
                'video_rights': 'Monetized Allowed',
                'royalty_payment': 'None',
            },
            {
                'license_type_name': 'Exclusive License',
                'license_template': 'Exclusive license agreement template...',
                'license_term': 'Unlimited',
                'transferability': 'Transferable',
                'price': Decimal('499.99'),
                'download_limit': 'Unlimited',
                'streaming_limit': 'Unlimited',
                'monetized_radio_plays': 'Unlimited',
                'video_rights': 'Full Rights',
                'royalty_payment': 'None',
            },
        ]
        
        self.license_types = []
        for lt in license_types:
            license_type, _ = License_type.objects.get_or_create(
                license_type_name=lt['license_type_name'],
                defaults=lt
            )
            self.license_types.append(license_type)

    def create_track_license_options(self):
        """Create track license options (link tracks to license types)"""
        self.stdout.write('  Creating track license options...')
        
        # Create a dummy storage file for each track
        for track in self.tracks:
            storage_file, _ = TrackStorageFile.objects.get_or_create(
                description=f'{track.title} - Main Mix',
                file_format=self.wav_format,
                defaults={
                    # 'file_path': track._file_path,
                    'bit_rate': 1411,
                    'file_size': 30000000,
                }
            )
            with open(track._file_path, 'rb') as f:
                storage_file.file_path.save(os.path.basename(track._file_path), File(f))
            
            # Link each track to all license types
            for license_type in self.license_types:
                TrackLicenseOptions.objects.get_or_create(
                    track=track,
                    track_storage_file=storage_file,
                    license_type=license_type,
                )

    # def create_buyers(self):
    #     """Create test buyers"""
    #     self.stdout.write('  Creating buyers...')
        
    #     buyer_contact, _ = Contact.objects.get_or_create(
    #         email='buyer@example.com',
    #         defaults={
    #             'first_name': 'Test',
    #             'last_name': 'Buyer',
    #             'contact_type': Contact.ContactType.INDIVIDUAL,
    #         }
    #     )
        
    #     Address.objects.get_or_create(
    #         contact=buyer_contact,
    #         address_type=Address.AddressType.BILLING,
    #         defaults={
    #             'address_line_1': '456 Customer St',
    #             'city': 'New York',
    #             'state_province': 'NY',
    #             'postal_code': '10001',
    #             'country': 'USA',
    #         }
    #     )
        
    #     self.buyer, _ = Buyer.objects.get_or_create(
    #         contact=buyer_contact,
    #     )
