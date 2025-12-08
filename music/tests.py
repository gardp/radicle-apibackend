from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Track, FileFormat, TrackStorageFile, Library, MusicProfessional, Contributor, SocialMediaLink, Contribution, Publisher, Publishing
import uuid
from common.models import Contact
from custom_users.models import CustomUser

class TrackAPITestCase(APITestCase):
    def setUp(self):
        """Set up the test client and create a track instance."""

        self.track = Track.objects.create(
            track_id=uuid.uuid4(),
            title="Test Track",
            duration_seconds=120
        )

    def test_list_tracks(self):
        """Ensure we can list tracks."""
        url = reverse('tracks-list') # Assuming your URL name is 'track-list'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Track')

    def test_retrieve_track(self):
        """Ensure we can retrieve a single track."""
        url = reverse('tracks-detail', kwargs={'pk': self.track.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Track')

class FileFormatAPITestCase(APITestCase):
    def setUp(self):
        """Set up the test client and create a file format instance."""
        self.file_format = FileFormat.objects.create(
            name="Test Format",
            mime_type="audio/test",
            extension=".test",
            codec="Test Codec",
            compression="lossless",
            bit_depth=16,
            sample_rate=44100,
            file_size_factor=1.00,
            active=True
        )

    def test_list_file_formats(self):
        """Ensure we can list file formats."""
        url = reverse('file-formats-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Format')

    def test_retrieve_file_format(self):
        """Ensure we can retrieve a single file format."""
        url = reverse('file-formats-detail', kwargs={'pk': self.file_format.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Format')


class TrackStorageFileAPITestCase(APITestCase):
    def setUp(self):
        """Set up the test client and create a track storage file instance."""
        self.file_format = FileFormat.objects.create(
            name="Test Format",
            mime_type="audio/test",
            extension=".test",
            codec="Test Codec",
            compression="lossless",
            bit_depth=16,
            sample_rate=44100,
            file_size_factor=1.00,
            active=True
        )
        self.track_storage_file = TrackStorageFile.objects.create(
            track_storage_file_id=uuid.uuid4(),
            file_path="test_file_path",
            file_format=self.file_format,
            bit_rate=128,
            file_size=1024
        )
        
    def test_list_track_storage_files(self):
        """Ensure we can list track storage files."""
        url = reverse('track-storage-files-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn('test_file_path', response.data[0]['file_path'])

    def test_retrieve_track_storage_file(self):
        """Ensure we can retrieve a single track storage file."""
        url = reverse('track-storage-files-detail', kwargs={'pk': self.track_storage_file.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('test_file_path', response.data['file_path'])

class LibraryAPITestCase(APITestCase):
    def setUp(self):
        """Set up the test client and create a library instance."""
        # self.contact = Contact.objects.create(
        #     contact_id=uuid.uuid4(),
        #     first_name="Test",
        #     last_name="Contact",
        #     email="test_contact@example.com"
        # )
        self.custom_user = CustomUser.objects.create_user(
            username="test_contact@example.com",
            email="test_contact@example.com"
        )
        self.track = Track.objects.create(
            track_id=uuid.uuid4(),
            title="Test Track",
            duration_seconds=120
        )
        self.library = Library.objects.create(
            library_id=uuid.uuid4(),
            library_owner=self.custom_user,
            library_name="Test Library"
        )
    
    def test_list_libraries(self):
        """Ensure we can list libraries."""
        url = reverse('libraries-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['library_name'], 'Test Library')
    
    def test_retrieve_library(self):
        """Ensure we can retrieve a single library."""
        url = reverse('libraries-detail', kwargs={'pk': self.library.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['library_name'], 'Test Library')

class MusicProfessionalAPITestCase(APITestCase):
    def setUp(self):
        """Set up the test client and create a music professional instance."""
        self.contact = Contact.objects.create(
            contact_id=uuid.uuid4(),
            first_name="Test",
            last_name="Contact",
            email="test_contact@example.com"
        )
        self.music_professional = MusicProfessional.objects.create(
            professional_id=uuid.uuid4(),
            contact=self.contact,
            ref_code="TEST123",
            pro_affiliation="ASCAP",
            ipi_number="1234567890",
            note="Test music professional"
        )
    
    def test_list_music_professionals(self):
        """Ensure we can list music professionals."""
        url = reverse('music-professionals-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['ref_code'], 'TEST123')
    
    def test_retrieve_music_professional(self):
        """Ensure we can retrieve a single music professional."""
        url = reverse('music-professionals-detail', kwargs={'pk': self.music_professional.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ref_code'], 'TEST123')

class ContributorAPITestCase(APITestCase):
    def setUp(self):
        """Set up the test client and create a contributor instance."""
        self.contact = Contact.objects.create(
            contact_id=uuid.uuid4(),
            first_name="Test",
            last_name="Contact",
            email="test_contact@example.com"
        )
        self.music_professional = MusicProfessional.objects.create(
            professional_id=uuid.uuid4(),
            contact=self.contact,
            ref_code="TEST123",
            pro_affiliation="ASCAP",
            ipi_number="1234567890",
            note="Test music professional"
        )
        self.contributor = Contributor.objects.create(
            contributor_id=uuid.uuid4(),
            music_professional=self.music_professional,
            role="Composer",
            note="Test contributor"
        )
    
    def test_list_contributors(self):
        """Ensure we can list contributors."""
        url = reverse('contributors-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['role'], 'Composer')
    
    def test_retrieve_contributor(self):
        """Ensure we can retrieve a single contributor."""
        url = reverse('contributors-detail', kwargs={'pk': self.contributor.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'Composer')


class SocialMediaLinkAPITestCase(APITestCase):
    def setUp(self):
        """Set up the test client and create a social media link instance."""
        self.contact = Contact.objects.create(
            contact_id=uuid.uuid4(),
            first_name="Test",
            last_name="Contact",
            email="test_contact@example.com"
        )
        self.music_professional = MusicProfessional.objects.create(
            professional_id=uuid.uuid4(),
            contact=self.contact,
            ref_code="TEST123",
            pro_affiliation="ASCAP",
            ipi_number="1234567890",
            note="Test music professional"
        )
        self.contributor = Contributor.objects.create(
            contributor_id=uuid.uuid4(),
            music_professional=self.music_professional,
            role="Composer",
            note="Test contributor"
        )
        self.social_media_link = SocialMediaLink.objects.create(
            social_media_id=uuid.uuid4(),
            url="https://www.test.com",
            platform="Test Platform",
            contributor=self.contributor,
            music_professional=self.music_professional
        )
    
    def test_list_social_media_links(self):
        """Ensure we can list social media links."""
        url = reverse('social-media-links-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['url'], 'https://www.test.com')
    
    def test_retrieve_social_media_link(self):
        """Ensure we can retrieve a single social media link."""
        url = reverse('social-media-links-detail', kwargs={'pk': self.social_media_link.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['url'], 'https://www.test.com')


class ContributionAPITestCase(APITestCase):
    def setUp(self):
        """Set up the test client and create a contribution instance."""
        self.contact = Contact.objects.create(
            contact_id=uuid.uuid4(),
            first_name="Test",
            last_name="Contact",
            email="test_contact@example.com"
        )
        self.music_professional = MusicProfessional.objects.create(
            professional_id=uuid.uuid4(),
            contact=self.contact,
            ref_code="TEST123",
            pro_affiliation="ASCAP",
            ipi_number="1234567890",
            note="Test music professional"
        )
        self.contributor = Contributor.objects.create(
            contributor_id=uuid.uuid4(),
            music_professional=self.music_professional,
            role="Composer",
            note="Test contributor"
        )
        self.track = Track.objects.create(
            track_id=uuid.uuid4(),
            title="Test Track",
            duration_seconds=120
        )
        self.contribution = Contribution.objects.create(
            contribution_id=uuid.uuid4(),
            contribution_type="Composer",
            contribution_description="Test contribution description",
            contribution_date="2022-01-01",
            contributor=self.contributor,
            track=self.track
        )

    def test_list_contributions(self):
        """Ensure we can list contributions."""
        url = reverse('contributions-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['contribution_type'], 'Composer')
    
    def test_retrieve_contribution(self):
        """Ensure we can retrieve a single contribution."""
        url = reverse('contributions-detail', kwargs={'pk': self.contribution.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['contribution_type'], 'Composer')

class PublisherAPITestCase(APITestCase):
    def setUp(self):
        """Set up the test client and create a publisher instance."""
        self.contact = Contact.objects.create(
            contact_id=uuid.uuid4(),
            first_name="Test",
            last_name="Contact",
            email="test_contact@example.com"
        )
        self.publisher = Publisher.objects.create(
            publisher_id=uuid.uuid4(),
            contact=self.contact,
            website="https://www.test.com",
            pro_affiliation="ASCAP",
            note="Test publisher"
        )   
    
    def test_list_publishers(self):
        """Ensure we can list publishers."""
        url = reverse('publishers-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['pro_affiliation'], 'ASCAP')
    
    def test_retrieve_publisher(self):
        """Ensure we can retrieve a single publisher."""
        url = reverse('publishers-detail', kwargs={'pk': self.publisher.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pro_affiliation'], 'ASCAP') 

class PublishingAPITestCase(APITestCase):
    def setUp(self):
        """Set up the test client and create a publishing instance."""
        self.contact = Contact.objects.create(
            contact_id=uuid.uuid4(),
            first_name="Test",
            last_name="Contact",
            email="test_contact@example.com"
        )
        self.publisher = Publisher.objects.create(
            publisher_id=uuid.uuid4(),
            contact=self.contact,
            website="https://www.test.com",
            pro_affiliation="ASCAP",
            note="Test publisher"
        )
        self.publishing = Publishing.objects.create(
            publishing_id=uuid.uuid4(),
            publisher=self.publisher,
            track=self.track,
            contribution=self.contribution,
            note="Test publishing"
        )