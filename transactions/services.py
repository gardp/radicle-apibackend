import stripe
import paypalrestsdk
from django.conf import settings
from decimal import Decimal
from .models import Payment, PaymentStatus
import requests
from base64 import b64encode

stripe.api_key = settings.STRIPE_SECRET_KEY
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

# Line 16: })  <-- end of paypalrestsdk.configure

# Stripe process: PaymentIntent -> client_secret (save payment record) -> frontend -> confirmPaymentIntent
# PayPal process: get access token -> create order (save payment record) -> frontend -> approve order -> capture order
class PayPalClient:
    @staticmethod
    def get_access_token():
        """Get OAuth token from PayPal to create the paypal order with it"""
        auth = b64encode(
            f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}".encode()
        ).decode()
        
        response = requests.post(
            f"{PayPalClient.get_base_url()}/v1/oauth2/token",
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={"grant_type": "client_credentials"}
        )
        return response.json()["access_token"]
    
    @staticmethod
    def get_base_url(): #sendbox for test and simulation and live for production
        if settings.PAYPAL_MODE == "sandbox":
            return "https://api-m.sandbox.paypal.com"
        return "https://api-m.paypal.com"


class PaymentService:
    @staticmethod
    def create_stripe_payment(order, currency='USD'):
        """Create a Stripe payment intent for the order"""
        # CHECK FOR EXISTING PENDING PAYMENT RECORD FIRST
        existing_payment = Payment.objects.filter(
            order=order,
            provider='stripe',
            status=PaymentStatus.PENDING
        ).first()
    
        if existing_payment:
            # Retrieve the existing PaymentIntent to get client_secret
            stripe_intent = stripe.PaymentIntent.retrieve(existing_payment.provider_payment_id)
            return existing_payment, stripe_intent.client_secret
        # IF NO EXISTING PAYMENT RECORD, CREATE A NEW ONE
        try:
            stripe_intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),  # Convert to cents
                currency=currency.lower(),
                receipt_email=order.buyer.contact.email,
                metadata={
                    'order_id': str(order.order_id),
                    'reference_number': order.reference_number
                }
            )
            #   SAVE PAYMENT RECORD
            payment_record = Payment.objects.create(
                order=order,
                provider='stripe',
                provider_payment_id=stripe_intent.id,
                amount=order.total_amount,
                currency=currency,
                status=PaymentStatus.PENDING
            )
            return payment_record, stripe_intent.client_secret
        except stripe.error.StripeError as e:
            raise PaymentError(f"Stripe error: {str(e)}")

    @staticmethod
    def create_paypal_order(order, currency='USD'):
        # CHECK FOR EXISTING PENDING PAYMENT RECORD FIRST
        existing_payment = Payment.objects.filter(
            order=order,
            provider='paypal',
            status=PaymentStatus.PENDING
        ).first()
    
        if existing_payment:
            # Return existing payment instead of creating new one
            return existing_payment, existing_payment.provider_payment_id

        """Create a PayPal order for smart buttons with the access token"""
        access_token = PayPalClient.get_access_token()
        #CREATING ORDER AFTER GETTING ACCESS TOKEN
        response = requests.post(
            f"{PayPalClient.get_base_url()}/v2/checkout/orders",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json={
            "intent": "CAPTURE",
            "purchase_units": [{
                "reference_id": order.reference_number,
                "amount": {
                    "currency_code": currency.upper(),
                    "value": f"{order.total_amount:.2f}"
                },
                "description": f"Order {order.reference_number}"
            }]
        }
        )
        if response.status_code == 201:
            paypal_order_id = response.json()["id"]
            #SAVE THE PAYMENT RECORD
            payment_record = Payment.objects.create(
            order=order,
            provider='paypal',
            provider_payment_id=paypal_order_id,
            amount=order.total_amount,
            currency=currency,
            status=PaymentStatus.PENDING
        )
            return payment_record, paypal_order_id 
        else:
            raise PaymentError(f"PayPal order creation error: {response.text}")    

    @staticmethod
    def capture_paypal_order(paypal_order_id):
        """Capture an approved PayPal Order via v2 API"""
        access_token = PayPalClient.get_access_token()
    
        response = requests.post(
            f"{PayPalClient.get_base_url()}/v2/checkout/orders/{paypal_order_id}/capture",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    )
    
        data = response.json()
        if response.status_code == 201 and data.get("status") == "COMPLETED":
            return data
        else:
            raise PaymentError(f"PayPal capture error: {data}")
   