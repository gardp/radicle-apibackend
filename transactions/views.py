from rest_framework import viewsets, permissions
from .models import Order, OrderItem, Payment, Receipt, Buyer
from .serializers import OrderSerializer, OrderItemSerializer, PaymentSerializer, ReceiptSerializer, BuyerSerializer
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from transactions.services import PaymentService
from django.conf import settings
from common.models import Contact, Address
from music.models import Contributor, Contribution, Track, MusicProfessional, SocialMediaLink
from licenses.models import License, License_type, LicenseHolding, Licensee, LicenseStatus, TrackLicenseOptions
from transactions.models import Order, OrderItem, Payment, PaymentStatus, Receipt, Buyer
import stripe
from decimal import Decimal
from datetime import datetime
class DebugLoggingMixin:
    """
    A mixin that provides simple print-based logging for DRF ViewSet actions.
    """
    def _log_request(self, action_name):
        print(f"DEBUG: {self.__class__.__name__}.{action_name} called")
        print(f"DEBUG: Request: {self.request.method} {self.request.path}")
        if self.request.query_params:
            print(f"DEBUG: Query params: {self.request.query_params}")
        if self.request.data:
            print(f"DEBUG: Request data: {self.request.data}")

    def list(self, request, *args, **kwargs):
        self._log_request('list')
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self._log_request('create')
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self._log_request('retrieve')
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._log_request('update')
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self._log_request('partial_update')
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self._log_request('destroy')
        return super().destroy(request, *args, **kwargs)


class OrderViewSet(DebugLoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint for Orders with debug logging.
    Permissions are open for development purposes.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):
        """
        Atomic checkout endpoint - creates entire order with licenses in one transaction.
        
        Handles:
        - Idempotency via reference_number
        - Full rollback on any failure
        - Returns order with license download links
        
        Request body structure:
        {
          "reference_number": "ORD-20251005-ABC12",
          "contributor_contact": {...},
          "contributor": {...},
          "shipping_address": {...},
          "buyer_contact": {...},
          "billing_address": {...},
          "items": [
            {
              "track_id": "uuid",
              "license_type_id": "uuid",
              "price": "29.99",
              "quantity": 1,
              "contributors": [
                {"contributor_id": "uuid", "contribution_type": "Composer"},
                ...
              ]
            }
          ],
          "payment": {
            "amount": "29.99",
            "processor": "creditCard",
            "provider_payment_id": "TXN123"
          }
        }
        """
        data = request.data
        reference_number = request.headers.get('Idempotency-Key')
        print("reference_number", reference_number) #for idempotency and order tracking 
        print("data", data)
        
        # Validate required top-level fields
        if not reference_number:
            return Response(
                {"reference_number": ["This field is required for idempotency."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # IDEMPOTENCY: Check if order already exists
        existing_order = Order.objects.filter(reference_number=reference_number).first()
        if existing_order:
            return Response(
                {
                    "message": "Order already exists with this reference number.",
                    "order_id": str(existing_order.order_id),
                    "reference_number": existing_order.reference_number,
                    "status": existing_order.status,
                    "created_at": existing_order.created_at,
                },
                status=status.HTTP_200_OK
            )
        
        # Validate required sections
        required_sections = ["licenseeContact", "musicProfessional", "buyerContact", "mailingRegistrationAddress", 
                           "billingAddress", "items"]
        missing = [s for s in required_sections if s not in data]
        if missing:
            return Response(
                {"detail": f"Missing required sections: {', '.join(missing)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not data["items"]:
            return Response(
                {"items": ["At least one item is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # ********LICENSEE********
                print("********LICENSEE********")
                # 1. Create licensee contact
                licensee_contact_data = data["licenseeContact"]
                licensee_contact = Contact(**licensee_contact_data)
                licensee_contact.full_clean()  # Validate before saving
                licensee_contact.save ()

                # 2. Get and create music professional(optional) and add the contact to it
                music_professional = data["musicProfessional"] #ref_code, proaffiliation....etc
                music_professional["contact"] = licensee_contact #passing the contact of the licensee to the music professional
                music_professional = MusicProfessional.objects.create(**music_professional)
                
                # 2. Create licensee
                licensee = Licensee.objects.create(music_professional=music_professional)
                # 2. Now get licensee/registration/mailing address, add contact and create
                mailing_registration_address = Address.objects.create(
                    **data["mailingRegistrationAddress"],
                    contact = licensee_contact,
                )
                
                # Social Media Links (optional)
                if "socialMediaLinks" in data and data["socialMediaLinks"]:
                    print("Social Media Links:", data["socialMediaLinks"])
                    social_media_dict = data["socialMediaLinks"]
                    for url in social_media_dict["url"]:
                        SocialMediaLink.objects.create(url=url, music_professional=music_professional)

                # ****BUYER****
                # 4. Create buyer contact
                buyer_contact_data = data["buyerContact"]
                buyer_contact = Contact(**buyer_contact_data)
                buyer_contact.full_clean()  # Validate before saving
                buyer_contact.save()
                
                # 5. Create billing address 
                billing_address_data = data["billingAddress"].copy()
                billing_address_data["contact"] = buyer_contact
                billing_address = Address.objects.create(**billing_address_data)
                
                # 6. Create buyer
                buyer = Buyer.objects.create(
                    contact=buyer_contact
                )

                # ****ORDER****
                # 7. Create an order variable that takes all the license prices and quantity in the backend to create the order in the backend instead so as it's safer from user tampering
                subtotal = 0
                for item_data in data["items"]:
                    # get the track license option from each track
                    track_license_option = TrackLicenseOptions.objects.get(track_license_option_id=item_data["track_license_option_id"])
                    # get the license price from the track license option
                    license_price = track_license_option.license_type.price
                    # get the quantity from the item data
                    quantity = item_data["quantity"]
                    # calculate the total price for the item
                    total_price = license_price * quantity
                    # add the total price to the subtotal
                    subtotal += total_price
                # create the order with the subtotal as the total amount the tax amount is calculated in the model
                order = Order.objects.create(
                    reference_number=reference_number,
                    buyer=buyer,
                    status=Order.OrderStatus.PENDING,
                    subtotal=subtotal,
                    currency="usd",
                )
            
                # ****LICENSE****
                # 9. Process each cart item license
                created_licenses = []
                holdings = []
                for item_data in data["items"]:
                    track_id = item_data.get("track_id")
                    track_license_option_id = item_data.get("track_license_option_id")
                    # It's more secure to get the price of each license in the backend to that users don't temper with it
                    track_license_option = TrackLicenseOptions.objects.get(track_license_option_id=track_license_option_id)
                    price = track_license_option.license_type.price
                    # get the quantity from the item data
                    quantity = item_data.get("quantity", 1)
                    print("my track_id", track_id)
                    # Validate track and license_type exist
                    try:
                        track = Track.objects.get(track_id=track_id)
                        track_license_option = TrackLicenseOptions.objects.get(track_license_option_id=track_license_option_id)
                    except Track.DoesNotExist:
                        raise ValueError(f"Track {track_id} not found")
                    except TrackLicenseOptions.DoesNotExist:
                        raise ValueError(f"Track license option {track_license_option_id} not found")
                    
                    # ****ORDERITEM****
                    # Create orderItem (generic FK to track_license_option instead of license) as it will be used to create the license
                    # License is typically a derived artifact that can change state over time.
                    # *License represents fulfillment generated from that purchase.
                    # *TrackLicenseOption is the product being purchased.
                    content_type = ContentType.objects.get(app_label='licenses', model='tracklicenseoptions')
                    order_item = OrderItem.objects.create(
                        order=order,
                        content_type=content_type,
                        object_id=track_license_option.track_license_option_id,
                        quantity=quantity,
                        price=price
                    )
                    
                    # Create license - And MAKE SURE YO INCLUDE THE LICENSE_AGREEMENT_FILE LATER
                    license_obj = License.objects.create(
                        track_license_option=track_license_option,
                        order_item=order_item,
                    ) 
                    #TODO: Automate expiration date
                    
                    # ****LICENSEHOLDING****
                    # Create license holdings for each licensee
                    # Create license holding
                    holding = LicenseHolding.objects.create(
                        license=license_obj,
                        licensee=licensee, #from the created licensee above
                    )

                    # Create license status
                    license_status = LicenseStatus.objects.create(
                        license=license_obj,
                        license_status_option='Active',
                        license_status_date=timezone.now(),
                    )
                    
                    created_licenses.append({
                        "license_id": str(license_obj.license_id),
                        "track_id": str(track.track_id),
                        "track_title": track.title,
                        "license_type": track_license_option.license_type.license_type_name,
                        "download_url": license_obj.license_agreement_file.url if license_obj.license_agreement_file else None,
                    })
                holdings.append({
                    "licensee_id": str(licensee.licensee_id),
                    "licensee_name": f"{licensee.music_professional.contact.first_name} {licensee.music_professional.contact.last_name}".strip(),
                    "licensee_email": licensee.music_professional.contact.email,
                    "transaction_id": str(order.order_id),
                    "reference_number": order.reference_number ,
                    "created_at": order.created_at,
                    "buyer_id": str(buyer.buyer_id),
                    "buyer_name": f"{buyer.contact.first_name} {buyer.contact.last_name}".strip(),
                    "buyer_email": buyer.contact.email,
                    "amount": str(order.total_amount),
                    "status": order.status,
                    "licenses": created_licenses
                })

                # Success - return complete response
                return Response({
                    "order_id": str(order.order_id),
                    "reference_number": order.reference_number,
                    "status": order.status,
                    "total_amount": str(order.total_amount),
                    "currency": order.currency,
                    "subtotal": str(order.subtotal),
                    "tax_rate": str(order.tax_rate),
                    "tax_amount": str(order.tax_amount),
                    "created_at": order.created_at,
                    "buyer": {
                        "buyer_id": str(buyer.buyer_id),
                        "buyer_name": f"{buyer.contact.first_name} {buyer.contact.last_name}".strip(),
                        "buyer_email": buyer.contact.email
                    },
                    "license_holdings": holdings,


                    "message": "Order completed successfully. Licenses created and ready for download."
                }, status=status.HTTP_201_CREATED)
            print("Order Response: ", response.data)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Checkout failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderItemViewSet(DebugLoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint for OrderItems with debug logging.
    Permissions are open for development purposes.
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class PaymentViewSet(DebugLoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint for Payments with debug logging.
    Permissions are open for development purposes.
    """
    @action(detail=False, methods=['post'])
    def create_payment_intent(self, request):
        data = request.data
        reference_number = request.headers.get('Idempotency-Key')
        print("reference_number", reference_number)
        print("payment intent data", data)
    
    # Validate required top-level fields
        if not reference_number:
            return Response(
                {"reference_number": ["This field is required for idempotency."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            order_id = data.get('order_id')
            provider = data.get('provider')
            currency = data.get('currency')
            
            order = Order.objects.get(order_id=order_id)
            
            if provider == 'stripe':
                # creating the payment intent using the payment parameters in create_stripe_payment
                payment_intent, client_secret = PaymentService.create_stripe_payment(
                    order=order,
                    currency=currency
                )
                return Response({
                    'client_secret': client_secret,
                    'stripe_intent_id': payment_intent.provider_payment_id,
                    'publishable_key': settings.STRIPE_PUBLISHABLE_KEY
                })
            
            elif provider == 'paypal':
                # creating the payment intent using the payment parameters in create_paypal_order
                payment_intent, paypal_order_id = PaymentService.create_paypal_order(
                    order=order,
                    currency=currency,
                )

                return Response({
                    'paypal_order_id': paypal_order_id, #This is the paypal order id as it's saved in the database record payment table
                })
                
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def capture_paypal_order(self, request):
        paypal_order_id = request.data.get('paypal_order_id')
    
        if not paypal_order_id:
            return Response(
                {'error': 'paypal_order_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
        try:
            # Find your payment record
            payment = Payment.objects.get(
                provider='paypal',
                provider_payment_id=paypal_order_id
            )
        
            # Capture via PayPal
            capture_data = PaymentService.capture_paypal_order(paypal_order_id)
        
            # Update statuses and fulfill licenses after transaction commits for idempotency for PayPal
            with transaction.atomic():
                payment.status = PaymentStatus.SUCCESS
                payment.save()

                order = payment.order
                order.status = Order.OrderStatus.COMPLETED
                order.save()
                print("Order status updated- now fulfilling order licenses")
                # Fulfill order licenses after transaction commits asynchronously using Celery
                transaction.on_commit(lambda: fulfill_order_licenses.delay(str(order.order_id)))
        
            # Send confirmation - to set up later for more email customization
            # send_purchase_confirmation(order)
        
            return Response({
                'status': 'success',
                'order_id': str(order.order_id),
                'reference_number': order.reference_number
            })
        
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    # Stripe Webhook for handling payment events
    @action(detail=False, methods=['post'])
    def webhook(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        print("Order status updated- now fulfilling order licenses")
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            # Invalid payload
            return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle specific event types
        if event['type'] == 'payment_intent.succeeded':
            payment_intent_data = event['data']['object']
            
            try:
                payment = Payment.objects.get(
                    provider='stripe',
                    provider_payment_id=payment_intent_data['id']
                )
                
                with transaction.atomic():
                    payment.status = PaymentStatus.SUCCESS
                    payment.save()
                    
                    order = payment.order
                    order.status = Order.OrderStatus.COMPLETED
                    order.save()
                    #******* Fulfill STRIPE order licenses after transaction commits asynchronously using Celery    
                    transaction.on_commit(lambda: __import__("licenses.tasks").tasks.fulfill_order_licenses.delay(str(order.order_id)))

                # Send confirmation - to set up later for more email customization
                # send_purchase_confirmation(order)
                
            except Payment.DoesNotExist:
                return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent_data = event['data']['object']
            
            try:
                payment = Payment.objects.get(
                    provider='stripe',
                    provider_payment_id=payment_intent_data['id']
                )
                payment.status = PaymentStatus.FAILED
                payment.save()
                
                order = payment.order
                order.status = Order.OrderStatus.FAILED
                order.save()
                
            except Payment.DoesNotExist:
                pass  # Payment not found, ignore
        
        # Return 200 for all events (Stripe expects this)
        return Response({'status': 'success'})


class ReceiptViewSet(DebugLoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint for Receipts with debug logging.
    Permissions are open for development purposes.
    """
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class BuyerViewSet(DebugLoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint for Buyers with debug logging.
    Permissions are open for development purposes.
    """
    queryset = Buyer.objects.all()
    serializer_class = BuyerSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


# getting the content type of models to create GenericForein key for OrderItems models@api_view(['GET'])
class ContentTypeMappingViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]  # Adjust as needed
    
    def list(self, request):
        mappings = {}
        models_to_include = [
            ('music', 'track'),
            # Add other models
        ]
        
        for app_label, model in models_to_include:
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model)
                mappings[f"{app_label}.{model}"] = {
                    'id': ct.id,
                    'name': model.capitalize()
                }
            except ContentType.DoesNotExist:
                continue
        
        return Response(mappings)