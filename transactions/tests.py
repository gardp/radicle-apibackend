from django.test.utils import isolate_apps
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Buyer, Order, OrderItem, Payment, Receipt
from common.models import Contact
from licenses.models import License
from music.models import Track
from django.contrib.contenttypes.models import ContentType
import uuid
from django.db import models
from datetime import date
# Define a simple, test-only model to act as a purchasable item.
# This avoids pulling in dependencies from other apps like 'tracks' or 'licenses'.
 # This ensures the model is only used for tests and not created in the real database.
    
class BuyerTest(APITestCase):
    def setUp(self):
        self.contact = Contact.objects.create(first_name='Buyer', last_name='Buyer')
        self.buyer = Buyer.objects.create(contact=self.contact)
    
    def test_list_buyers(self):
        url = reverse('buyers-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data[0]['contact']), str(self.contact.contact_id))
        self.assertEqual(str(response.data[0]['buyer_id']), str(self.buyer.buyer_id))
    
    def test_retrieve_buyer(self):
        url = reverse('buyers-detail', kwargs={'pk': self.buyer.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['contact']), str(self.contact.contact_id))
        self.assertEqual(str(response.data['buyer_id']), str(self.buyer.buyer_id))


class OrderTest(APITestCase):
    def setUp(self):
        self.contact = Contact.objects.create(first_name='Buyer', last_name='Buyer')
        self.buyer = Buyer.objects.create(contact=self.contact)
        self.order = Order.objects.create(buyer=self.buyer, reference_number='123456', total_amount=100.00)
    
    def test_list_orders(self):
        url = reverse('orders-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data[0]['buyer']), str(self.buyer.buyer_id))
        self.assertEqual(str(response.data[0]['reference_number']), '123456')
        self.assertEqual(str(response.data[0]['total_amount']), '100.00')
    
    def test_retrieve_order(self):
        url = reverse('orders-detail', kwargs={'pk': self.order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['buyer']), str(self.buyer.buyer_id))
        self.assertEqual(str(response.data['reference_number']), '123456')
        self.assertEqual(str(response.data['total_amount']), '100.00')

class OrderItemTest(APITestCase):
    def setUp(self):
        self.contact = Contact.objects.create(first_name='Buyer', last_name='Buyer')
        self.buyer = Buyer.objects.create(contact=self.contact)
        self.order = Order.objects.create(buyer=self.buyer, reference_number='123456', total_amount=100.00)
        self.track = Track.objects.create(title='Test Track')
        self.object_id = self.track.track_id
        self.content_type = ContentType.objects.get_for_model(Track)
        self.order_item = OrderItem.objects.create(order=self.order, quantity=1, price=100.00, content_type=self.content_type, object_id=self.object_id)
    
    def test_list_order_items(self):
        url = reverse('order-items-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data[0]['order']), str(self.order.order_id))
        self.assertEqual(str(response.data[0]['quantity']), '1')
        self.assertEqual(str(response.data[0]['price']), '100.00')
    
    def test_retrieve_order_item(self):
        url = reverse('order-items-detail', kwargs={'pk': self.order_item.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['order']), str(self.order.order_id))
        self.assertEqual(str(response.data['quantity']), '1')
        self.assertEqual(str(response.data['price']), '100.00')

class PaymentTest(APITestCase):
    def setUp(self):
        self.contact = Contact.objects.create(first_name='Buyer', last_name='Buyer')
        self.buyer = Buyer.objects.create(contact=self.contact)
        self.order = Order.objects.create(buyer=self.buyer, reference_number='123456', total_amount=100.00)
        self.payment = Payment.objects.create(order=self.order, amount=100.00, status='SUCCESS', processor='PayPal', transaction_id='123456')

    def test_list_payments(self):
        url = reverse('payments-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data[0]['order']), str(self.order.order_id))
        self.assertEqual(str(response.data[0]['amount']), '100.00')
        self.assertEqual(str(response.data[0]['status']), 'SUCCESS')
        self.assertEqual(str(response.data[0]['processor']), 'PayPal')
        self.assertEqual(str(response.data[0]['transaction_id']), '123456') 
    
    def test_retrieve_payment(self):
        url = reverse('payments-detail', kwargs={'pk': self.payment.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['order']), str(self.order.order_id))
        self.assertEqual(str(response.data['amount']), '100.00')
        self.assertEqual(str(response.data['status']), 'SUCCESS')
        self.assertEqual(str(response.data['processor']), 'PayPal')
        self.assertEqual(str(response.data['transaction_id']), '123456')
    
    
class ReceiptTest(APITestCase):
    def setUp(self):
        self.contact = Contact.objects.create(first_name='Buyer', last_name='Buyer')
        self.buyer = Buyer.objects.create(contact=self.contact)
        self.order = Order.objects.create(buyer=self.buyer, reference_number='123456', total_amount=100.00)
        self.payment = Payment.objects.create(order=self.order, amount=100.00, status='SUCCESS', processor='PayPal', transaction_id='123456')
        self.receipt = Receipt.objects.create(payment=self.payment, receipt_file='receipts/test.pdf')   
    
    def test_list_receipts(self):
        url = reverse('receipts-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data[0]['payment']), str(self.payment.payment_id))
        self.assertIn('receipts/test.pdf', response.data[0]['receipt_file'])

    def test_retrieve_receipt(self):
        url = reverse('receipts-detail', kwargs={'pk': self.receipt.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['payment']), str(self.payment.payment_id)) 
        self.assertIn('receipts/test.pdf', response.data['receipt_file'])