from rest_framework.test import APITestCase
from licenses.models import Copyright, CopyrightHolding, CopyrightStatus, License_type, Licensee, TrackLicenseOptions, License, LicenseHolding, LicenseStatus
import uuid
from rest_framework import status
from django.urls import reverse
from common.models import Contact
from music.models import Track, MusicProfessional, TrackStorageFile, FileFormat
from datetime import date, timedelta, timezone

class CopyrightTest(APITestCase):
    def setUp(self):
        self.track = Track.objects.create(
            track_id=uuid.uuid4(),
            title="Test Track",
            duration_seconds=120
        )
        self.copyright = Copyright.objects.create(
            copyright_id=uuid.uuid4(),
            copyright_type='Recording Copyright',
            description='Test Copyright',
            copyright_date=date.today(),
            track=self.track,
            note='Test Copyright Note'
        )
    def test_list_copyrights(self):
        url = reverse('copyrights-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['copyright_type'], 'Recording Copyright')
        self.assertEqual(response.data[0]['description'], 'Test Copyright')

    def test_retrieve_copyright(self):
        url = reverse('copyrights-detail', kwargs={'pk': self.copyright.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['copyright_type'], 'Recording Copyright')
        self.assertEqual(response.data['description'], 'Test Copyright')

class CopyrightHoldingTest(APITestCase):
    def setUp(self):
        self.track = Track.objects.create(
            track_id=uuid.uuid4(),
            title="Test Track",
            duration_seconds=120
        )
        self.copyright = Copyright.objects.create(
            copyright_id=uuid.uuid4(),
            copyright_type='Recording Copyright',
            description='Test Copyright',
            copyright_date=date.today(),
            track=self.track,
            note='Test Copyright Note'
        )
        self.contact = Contact.objects.create(
            contact_id=uuid.uuid4(),
            first_name="Test",
            last_name="Contact",
            email="test@example.com",
        )
        self.copyright_holder = MusicProfessional.objects.create(
            professional_id=uuid.uuid4(),
            contact=self.contact,
            ref_code="TEST123",
            pro_affiliation="ASCAP",
            ipi_number="1234567890",
            note="Test music professional"
        )
        self.copyright_holding = CopyrightHolding.objects.create(
            copyright_holding_id=uuid.uuid4(),
            copyright=self.copyright,
            copyright_holder=self.copyright_holder,
            copyright_holder_split=100,
            copyright_holding_note='Test Copyright Holding Note'
        )
    def test_list_copyrights(self):
        url = reverse('copyright-holdings-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['copyright_holding_note'], 'Test Copyright Holding Note')
        self.assertEqual(response.data[0]['copyright_holder_split'], 100)

    def test_retrieve_copyright(self):
        url = reverse('copyright-holdings-detail', kwargs={'pk': self.copyright_holding.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['copyright_holding_note'], 'Test Copyright Holding Note')
        self.assertEqual(response.data['copyright_holder_split'], 100)

class CopyrightStatusTest(APITestCase):
    def setUp(self):
        self.track = Track.objects.create(
            track_id=uuid.uuid4(),
            title="Test Track",
            duration_seconds=120
        )
        self.file_format = FileFormat.objects.create(
            name='Test File Format',
            mime_type='audio/mpeg',
            extension='.mp3',
            codec='MP3',
            compression='lossy',
            bit_depth=16,
            sample_rate=44100,
            file_size_factor=0.15,
            active=True
        )   
        self.track_storage_file = TrackStorageFile.objects.create(
            track_storage_file_id=uuid.uuid4(),
            file_format=self.file_format,
            bit_rate=128,
            file_size=1024,
        )
        self.copyright = Copyright.objects.create(
            copyright_id=uuid.uuid4(),
            copyright_type='Recording Copyright',
            description='Test Copyright',
            copyright_date=date.today(),
            track=self.track,
            note='Test Copyright Note'
        )
        self.copyright_status = CopyrightStatus.objects.create(
            copyright_status_id=uuid.uuid4(),
            copyright_status_option='Active',
            copyright_status_date=date.today(),
            copyright=self.copyright,
            copyright_status_note='Test Copyright Status Note'
        )
   
    def test_list_copyright_statuses(self):
        url = reverse('copyright-status-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['copyright_status_option'], 'Active')
        self.assertEqual(response.data[0]['copyright_status_date'], str(date.today()))
   
    def test_retrieve_copyright_status(self):
        url = reverse('copyright-status-detail', kwargs={'pk': self.copyright_status.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['copyright_status_option'], 'Active')
        self.assertEqual(response.data['copyright_status_date'], str(date.today()))
    
class LicenseTypeTest(APITestCase):
    def setUp(self):
        self.license_type = License_type.objects.create(
            license_type_id=uuid.uuid4(),
            license_type_name='Test License Type',
            license_template='Test License Template',
            license_term='Test License Term',
            transferability='Transferable',
            price=100.00,
            download_limit='Unlimited',
            streaming_limit='Unlimited',
            monetized_radio_plays='Unlimited',
            video_rights='Unlimited',
            royalty_payment='Unlimited',
            credit_requirement='Yes'
        )
    
    def test_list_license_types(self):
        url = reverse('license-types-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['license_type_name'], 'Test License Type')
        self.assertEqual(response.data[0]['license_template'], 'Test License Template')
        self.assertEqual(response.data[0]['license_term'], 'Test License Term')
        self.assertEqual(response.data[0]['transferability'], 'Transferable')
        self.assertEqual(response.data[0]['price'], '100.00')
        self.assertEqual(response.data[0]['download_limit'], 'Unlimited')
        self.assertEqual(response.data[0]['streaming_limit'], 'Unlimited')
        self.assertEqual(response.data[0]['monetized_radio_plays'], 'Unlimited')
        self.assertEqual(response.data[0]['video_rights'], 'Unlimited')
        self.assertEqual(response.data[0]['royalty_payment'], 'Unlimited')
        self.assertEqual(response.data[0]['credit_requirement'], 'Yes')

    def test_retrieve_license_type(self):
        url = reverse('license-types-detail', kwargs={'pk': self.license_type.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['license_type_name'], 'Test License Type')
        self.assertEqual(response.data['license_template'], 'Test License Template')
        self.assertEqual(response.data['license_term'], 'Test License Term')
        self.assertEqual(response.data['transferability'], 'Transferable')
        self.assertEqual(response.data['price'], '100.00')
        self.assertEqual(response.data['download_limit'], 'Unlimited')
        self.assertEqual(response.data['streaming_limit'], 'Unlimited')
        self.assertEqual(response.data['monetized_radio_plays'], 'Unlimited')
        self.assertEqual(response.data['video_rights'], 'Unlimited')
        self.assertEqual(response.data['royalty_payment'], 'Unlimited')
        self.assertEqual(response.data['credit_requirement'], 'Yes')


class LicenseeTest(APITestCase):
    def setUp(self):
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
        self.licensee = Licensee.objects.create(
            licensee_id=uuid.uuid4(),
            music_professional=self.music_professional,
            role="Composer",
            note="Test licensee"
        )
    
    def test_list_licensees(self):
        url = reverse('licensees-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['role'], 'Composer')
        self.assertEqual(response.data[0]['note'], 'Test licensee')

    def test_retrieve_licensee(self):
        url = reverse('licensees-detail', kwargs={'pk': self.licensee.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'Composer')
        self.assertEqual(response.data['note'], 'Test licensee')

class TrackLicenseOptionsTest(APITestCase):
    def setUp(self):
        self.track = Track.objects.create(
            track_id=uuid.uuid4(),
            title="Test Track",
            duration_seconds=120
        )
        self.file_format = FileFormat.objects.create(
            name='Test File Format',
            mime_type='audio/mpeg',
            extension='.mp3',
            codec='MP3',
            compression='lossy',
            bit_depth=16,
            sample_rate=44100,
            file_size_factor=0.15,
            active=True
        )
        self.track_storage_file = TrackStorageFile.objects.create(
            track_storage_file_id=uuid.uuid4(),
            file_format=self.file_format,
            bit_rate=128,
            file_size=1024,
        )
        self.license_type = License_type.objects.create(
            license_type_id=uuid.uuid4(),
            license_type_name='Test License Type',
            license_template='Test License Template',
            license_term='Test License Term',
            transferability='Transferable',
            price=100.00,
            download_limit='Unlimited',
            streaming_limit='Unlimited',
            monetized_radio_plays='Unlimited',
            video_rights='Unlimited',
            royalty_payment='Unlimited',
            credit_requirement='Yes'
        )
        self.track_license_option = TrackLicenseOptions.objects.create(
            track_license_option_id=uuid.uuid4(),
            track=self.track,
            track_storage_file=self.track_storage_file,
            license_type=self.license_type
        )
    def test_list_track_license_options(self):
        url = reverse('track-license-options-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['track_license_option_id'], str(self.track_license_option.track_license_option_id))
    def test_retrieve_track_license_option(self):
        url = reverse('track-license-options-detail', kwargs={'pk': self.track_license_option.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['track_license_option_id'], str(self.track_license_option.track_license_option_id))

class LicenseTest(APITestCase):
    def setUp(self):
        self.track = Track.objects.create(
            track_id=uuid.uuid4(),
            title="Test Track",
            duration_seconds=120
        )
        self.file_format = FileFormat.objects.create(
            name='Test File Format',
            mime_type='audio/mpeg',
            extension='.mp3',
            codec='MP3',
            compression='lossy',
            bit_depth=16,
            sample_rate=44100,
            file_size_factor=0.15,
            active=True
        )   
        self.track_storage_file = TrackStorageFile.objects.create(
            track_storage_file_id=uuid.uuid4(),
            file_format=self.file_format,
            bit_rate=128,
            file_size=1024,
        )
        self.license_type = License_type.objects.create(
            license_type_id=uuid.uuid4(),
            license_type_name='Test License Type',
            license_template='Test License Template',
            license_term='Test License Term',
            transferability='Transferable',
            price=100.00,
            download_limit='Unlimited',
            streaming_limit='Unlimited',
            monetized_radio_plays='Unlimited',
            video_rights='Unlimited',
            royalty_payment='Unlimited',
            credit_requirement='Yes'
        )
        self.track_license_option = TrackLicenseOptions.objects.create(
            track_license_option_id=uuid.uuid4(),
            track=self.track,
            track_storage_file=self.track_storage_file,
            license_type=self.license_type,
        )
        self.license = License.objects.create(
            license_id=uuid.uuid4(),
            track_license_option=self.track_license_option,
            expiration_date=date.today() + timedelta(days=365),
            license_note='Test license'
        )
    
    def test_list_licenses(self):
        url = reverse('licenses-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['license_id'], str(self.license.license_id))
        self.assertEqual(response.data[0]['license_note'], 'Test license')
    
    def test_retrieve_license(self):
        url = reverse('licenses-detail', kwargs={'pk': self.license.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['license_id'], str(self.license.license_id))
        self.assertEqual(response.data['license_note'], 'Test license')

class LicenseHoldingTest(APITestCase):
    def setUp(self):
        self.track = Track.objects.create(
            track_id=uuid.uuid4(),
            title="Test Track",
            duration_seconds=120
        )
        self.file_format = FileFormat.objects.create(
            name='Test File Format',
            mime_type='audio/mpeg',
            extension='.mp3',
            codec='MP3',
            compression='lossy',
            bit_depth=16,
            sample_rate=44100,
            file_size_factor=0.15,
            active=True
        )   
        self.track_storage_file = TrackStorageFile.objects.create(
            track_storage_file_id=uuid.uuid4(),
            file_format=self.file_format,
            bit_rate=128,
            file_size=1024,
        )
        self.license_type = License_type.objects.create(
            license_type_id=uuid.uuid4(),
            license_type_name='Test License Type',
            license_template='Test License Template',
            license_term='Test License Term',
            transferability='Transferable',
            price=100.00,
            download_limit='Unlimited',
            streaming_limit='Unlimited',
            monetized_radio_plays='Unlimited',
            video_rights='Unlimited',
            royalty_payment='Unlimited',
            credit_requirement='Yes'
        )
        self.track_license_option = TrackLicenseOptions.objects.create(
            track_license_option_id=uuid.uuid4(),
            track=self.track,
            track_storage_file=self.track_storage_file,
            license_type=self.license_type,
        )
        self.license = License.objects.create(
            license_id=uuid.uuid4(),
            track_license_option=self.track_license_option,
            expiration_date=date.today() + timedelta(days=365),
            license_note='Test license'
        )
        self.contact = Contact.objects.create(
            contact_id=uuid.uuid4(),
            first_name="Test",
            last_name="Contact",
            email="test@example.com"
        )
        self.music_professional = MusicProfessional.objects.create(
            professional_id=uuid.uuid4(),
            contact=self.contact,
            ref_code="TEST123",
            pro_affiliation="ASCAP",
            ipi_number="1234567890",
            note="Test music professional"
        )
        self.licensee = Licensee.objects.create(
            licensee_id=uuid.uuid4(),
            music_professional=self.music_professional,
            role="Composer",
            note="Test licensee"
        )
        self.license_holding = LicenseHolding.objects.create(
            license_holding_id=uuid.uuid4(),
            license=self.license,
            licensee=self.licensee,
            licensee_split=50,
            license_holding_note='Test license holding'
        )
    
    def test_list_license_holdings(self):
        url = reverse('license-holdings-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['license_holding_id'], str(self.license_holding.license_holding_id))
        self.assertEqual(str(response.data[0]['license']), str(self.license.license_id))
        self.assertEqual(str(response.data[0]['licensee']), str(self.licensee.licensee_id))
        self.assertEqual(response.data[0]['licensee_split'], 50)
        self.assertEqual(response.data[0]['license_holding_note'], 'Test license holding')
    
    def test_retrieve_license_holding(self):
        url = reverse('license-holdings-detail', kwargs={'pk': self.license_holding.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['license_holding_id'], str(self.license_holding.license_holding_id))
        self.assertEqual(str(response.data['license']), str(self.license.license_id))
        self.assertEqual(str(response.data['licensee']), str(self.licensee.licensee_id))
        self.assertEqual(response.data['licensee_split'], 50)
        self.assertEqual(response.data['license_holding_note'], 'Test license holding')

class LicenseStatusTest(APITestCase):
    def setUp(self):
        self.track = Track.objects.create(
            track_id=uuid.uuid4(),
            title="Test Track",
            duration_seconds=120
        )
        self.file_format = FileFormat.objects.create(
            name='Test File Format',
            mime_type='audio/mpeg',
            extension='.mp3',
            codec='MP3',
            compression='lossy',
            bit_depth=16,
            sample_rate=44100,
            file_size_factor=0.15,
            active=True
        )
        self.track_storage_file = TrackStorageFile.objects.create(
            track_storage_file_id=uuid.uuid4(),
            file_format=self.file_format,
            bit_rate=128,
            file_size=1024,
        )       
        self.license_type = License_type.objects.create(
            license_type_id=uuid.uuid4(),
            license_type_name='Test License Type',
            license_template='Test License Template',
            license_term='Test License Term',
            transferability='Transferable',
            price=100.00,
            download_limit='Unlimited',
            streaming_limit='Unlimited',
            monetized_radio_plays='Unlimited',
            video_rights='Unlimited',
            royalty_payment='Unlimited',
            credit_requirement='Yes'
        )
        self.track_license_option = TrackLicenseOptions.objects.create(
            track_license_option_id=uuid.uuid4(),
            track=self.track,
            track_storage_file=self.track_storage_file,
            license_type=self.license_type,
        )
        self.license = License.objects.create(
            license_id=uuid.uuid4(),
            track_license_option=self.track_license_option,
            expiration_date=date.today() + timedelta(days=365),
            license_note='Test license'
        )
        self.license_status = LicenseStatus.objects.create(
            license_status_id=uuid.uuid4(),
            license_status_option='Active',
            license_status_date=date.today(),
            license=self.license,
            license_status_note='Test license status'
        )
        
    def test_list_license_statuses(self):
        url = reverse('license-status-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['license_status_id'], str(self.license_status.license_status_id))
        self.assertEqual(response.data[0]['license_status_option'], 'Active')
        self.assertEqual(response.data[0]['license_status_note'], 'Test license status')
    
    def test_retrieve_license_status(self):
        url = reverse('license-status-detail', kwargs={'pk': self.license_status.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['license_status_id'], str(self.license_status.license_status_id))
        self.assertEqual(response.data['license_status_option'], 'Active')
        self.assertEqual(response.data['license_status_note'], 'Test license status')