from django.db import models
import uuid
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from common.models import Address


class Buyer(models.Model):
    """A buyer of a track"""
    # Link to the standard Django User model for login/authentication
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                help_text="The user account for this buyer, if they have one.")
    buyer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Core contact info
    contact = models.OneToOneField('common.Contact', on_delete=models.CASCADE, related_name='buyer')
    def __str__(self):
        return self.contact.first_name + " " + self.contact.last_name


class Order(models.Model):
    """An order of a track"""
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_number = models.CharField(max_length=25, unique=True, default="0000",
                                       help_text="Human-readable order reference for customers for frontend")
    buyer = models.ForeignKey(Buyer, on_delete=models.PROTECT, related_name='orders',
                              help_text="The buyer who placed the order.")
    
    status = models.CharField(max_length=10, choices=OrderStatus.choices, default=OrderStatus.COMPLETED)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id} by {self.buyer.buyer_id}"



class OrderItem(models.Model):
    """A generic order item that can reprensent a track or a merch item"""
    order_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    
    # Generic foreign key to the product being purchased (e.g., a Track, a Merch item)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField() # Assumes your product PKs are UUIDs
    purchased_item = GenericForeignKey('content_type', 'object_id')
    
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                help_text="Price of the item at the time of purchase.")

    def __str__(self):
        return f"{self.quantity}x of {self.purchased_item} in Order {self.order.order_id}"

# transactions/models.py (continued)
class PaymentStatus(models.TextChoices): #it's reused in Receipt
    SUCCESS = 'SUCCESS', 'Success'
    FAILED = 'FAILED', 'Failed'
class Payment(models.Model):
    """A payment for an order"""
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2) #it's the total payment amount of the order
    status = models.CharField(max_length=10, choices=PaymentStatus.choices)
    
    # Store the transaction ID from your payment gateway (e.g., Stripe's charge ID)
    processor = models.CharField(max_length=50, default='PayPal')
    transaction_id = models.CharField(max_length=25, unique=True)
    
    processing_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} for Order {self.order.order_id}"

#### Remove receipt and add the receipt file to the payment model
class Receipt(models.Model):
    """A receipt for a payment"""
    receipt_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='receipts')
    receipt_file = models.FileField(upload_to='receipts/', blank=True, null=True)
 
    def __str__(self):
        return f"Receipt {self.receipt_id} for Payment {self.payment.payment_id}"