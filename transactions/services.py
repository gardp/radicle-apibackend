import stripe
import paypalrestsdk
from django.conf import settings
from decimal import Decimal
from .models import Payment, PaymentStatus

stripe.api_key = settings.STRIPE_SECRET_KEY
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

class PaymentService:
    @staticmethod
    def create_stripe_payment(order, currency='USD'):
        try:
            stripe_intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),  # Convert to cents
                currency=currency.lower(),
                metadata={
                    'order_id': str(order.order_id),
                    'reference_number': order.reference_number
                }
            )
            
            return Payment.objects.create(
                order=order,
                provider='stripe',
                provider_payment_id=stripe_intent.id,
                amount=order.total_amount,
                currency=currency,
                status=PaymentStatus.PENDING
            ), stripe_intent.client_secret
        except stripe.error.StripeError as e:
            raise PaymentError(f"Stripe error: {str(e)}")

    @staticmethod
    def create_paypal_payment(order, currency='USD', return_url=None, cancel_url=None):
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": return_url,
                "cancel_url": cancel_url
            },
            "transactions": [{
                "amount": {
                    "total": str(order.total_amount),
                    "currency": currency
                },
                "description": f"Order {order.reference_number}"
            }]
        })

        if payment.create(): #create the payment object in the database to keep a record
            # now getting the first approval_url from the payment intent
            approval_url = next(
                (link.href for link in payment.links if link.rel == "approval_url"),
                None
            )
            return Payment.objects.create(
                order=order,
                provider='paypal',
                provider_payment_id=payment.id,
                amount=order.total_amount,
                currency=currency,
                status=PaymentStatus.PENDING
            ), approval_url
        else:
            raise PaymentError(f"PayPal error: {payment.error}")
    
    @staticmethod
    def execute_paypal_payment(payment_id, payer_id):
        """Capture an approved PayPal order"""
        payment = paypalrestsdk.Payment.find(payment_id)
    
        if payment.execute({"payer_id": payer_id}):
            return payment
        else:
            raise PaymentError(f"PayPal capture error: {payment.error}")