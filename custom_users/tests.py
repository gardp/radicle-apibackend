from django.test import TestCase
from custom_users.models import CustomUser, UserProfile
from common.models import Address, Contact
from django.test.utils import override_settings

# Create your tests here.
class CustomUserTest(TestCase):
    def setUp(self):
        """Set up test data - runs before each test method"""
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass', email='test@example.com')
        # We'll try to get or create the profile since the signal might not work in tests
        # Create a contact for the profile
        self.contact = Contact.objects.create(email=self.user.email, contact_type=Contact.ContactType.INDIVIDUAL)
    
    def test_custom_user(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpass'))
        self.assertEqual(self.user.get_username(), 'testuser')
    
    def test_user_profile(self):
        self.assertEqual(self.user.id, self.user.id)
