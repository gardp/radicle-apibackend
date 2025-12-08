from rest_framework.test import APITestCase
from common.models import Address, Contact
from rest_framework import status
from django.urls import reverse
# Create your tests here.
class AddressTestCase(APITestCase):
    def setUp(self):
        self.contact = Contact.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="123-456-7890",
            contact_type=Contact.ContactType.INDIVIDUAL
        )
        self.address = Address.objects.create(
            address_line_1="123 Main St",
            city="Anytown",
            state_province="CA",
            postal_code="12345",
            country="USA",
            contact=self.contact
        )
    
    #Act
    def test_address_creation(self):
        url = reverse('addresses-list')
        response = self.client.get(url, format='json')
    
    #Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['address_line_1'], "123 Main St")
        self.assertEqual(response.data[0]['city'], "Anytown")
        self.assertEqual(response.data[0]['state_province'], "CA")
        self.assertEqual(response.data[0]['postal_code'], "12345")
        self.assertEqual(response.data[0]['country'], "USA")
        self.assertEqual(response.data[0]['contact'], self.contact.contact_id)
    
    def test_address_retrieval(self):
        url = reverse('addresses-detail', kwargs={'pk': self.address.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['address_line_1'], "123 Main St")
        self.assertEqual(response.data['city'], "Anytown")
        self.assertEqual(response.data['state_province'], "CA")
        self.assertEqual(response.data['postal_code'], "12345")
        self.assertEqual(response.data['country'], "USA")

class ContactTestCase(APITestCase):
    def setUp(self):
        # self.address = Address.objects.create(
        #     address_line_1="123 Main St",
        #     city="Anytown",
        #     state_province="CA",
        #     postal_code="12345",
        #     country="USA"
        # )
        self.contact = Contact.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="123-456-7890",
            # address=self.address,
            contact_type=Contact.ContactType.INDIVIDUAL
        )
    
    #Act
    def test_contact_creation(self):
        url = reverse('contacts-list')
        response = self.client.get(url, format='json')
    
    #Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], "John")
        self.assertEqual(response.data[0]['last_name'], "Doe")
        self.assertEqual(response.data[0]['email'], "john.doe@example.com")
        self.assertEqual(response.data[0]['phone_number'], "123-456-7890")
    
    def test_contact_retrieval(self):
        url = reverse('contacts-detail', kwargs={'pk': self.contact.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], "John")
        self.assertEqual(response.data['last_name'], "Doe")
        self.assertEqual(response.data['email'], "john.doe@example.com")
        self.assertEqual(response.data['phone_number'], "123-456-7890")