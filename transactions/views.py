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
from licenses.tasks import fulfill_order_licenses
from transactions.models import Order, OrderItem, Payment, PaymentStatus, Receipt, Buyer
import stripe
from decimal import Decimal
from datetime import datetime
from licenses.tasks import fulfill_order_licenses
from licenses.services import get_or_create_license_zip
from django.urls import reverse


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
        # if existing_order:
        #     return Response(
        #         {
        #             "message": "Order already exists with this reference number.",
        #             "order_id": str(existing_order.order_id),
        #             "reference_number": existing_order.reference_number,
        #             "status": existing_order.status,
        #             "created_date": existing_order.created_date,
        #         },
        #         status=status.HTTP_200_OK
        #     )
        
        # Validate required sections
        required_sections = ["licenseeContact", "musicProfessional", "buyerContact", "mailingRegistrationAddress", "billingAddress", "items"]
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
                licensee_contact, _ = Contact.objects.update_or_create(
                    email=licensee_contact_data["email"],
                    first_name=licensee_contact_data.get("first_name"),
                    last_name=licensee_contact_data.get("last_name"),
                    defaults={
                        "sudo_name" : licensee_contact_data.get("sudo_name"),
                        "company_name" : licensee_contact_data.get("company_name"),
                        "phone_number" : licensee_contact_data.get("phone"),
                    }
                )
                print("licensee_contact", licensee_contact)
                # licensee_contact.full_clean()  not needed fo rupdate and create...only for create

                # 2. Get and create music professional(optional) and add the contact to it
                music_professional_data = data["musicProfessional"] #ref_code, proaffiliation....etc
                music_professional_data["contact"] = licensee_contact #passing the contact of the licensee to the music professional
                music_professional, _ = MusicProfessional.objects.update_or_create(
                    contact=licensee_contact,
                    defaults={
                        "ref_code": music_professional_data.get("ref_code"),
                        "pro_affiliation": music_professional_data.get("pro_affiliation"),
                        "ipi_number": music_professional_data.get("ipi_number"),
                    }
                )
                
                # 3. Create licensee
                licensee, _ = Licensee.objects.update_or_create(
                    music_professional=music_professional,
                    defaults={}
                )


                # 4. Now get licensee/registration/mailing address, add contact and create
                mailing_registration_address_data = data["mailingRegistrationAddress"]
                mailing_registration_address, _ = Address.objects.update_or_create(
                    contact = licensee_contact,
                    defaults={
                        "address_line_1": mailing_registration_address_data["address_line_1"],
                        "address_line_2": mailing_registration_address_data["address_line_2"],
                        "city": mailing_registration_address_data["city"],
                        "state_province": mailing_registration_address_data["state_province"],
                        "postal_code": mailing_registration_address_data["postal_code"],
                        "country": mailing_registration_address_data["country"]
                    }
                )
                
                # Social Media Links (optional)
                if "socialMediaLinks" in data and data["socialMediaLinks"]:
                    print("Social Media Links:", data["socialMediaLinks"])
                    social_media_dict = data["socialMediaLinks"]
                    for url in social_media_dict:
                        SocialMediaLink.objects.update_or_create(
                            url=url,
                            music_professional=music_professional,
                            defaults={}
                        )

                # ****BUYER****
                # 4. update or create buyer contact
                buyer_contact_data = data["buyerContact"]
                buyer_contact, _ = Contact.objects.update_or_create(
                    email=buyer_contact_data["email"],
                    first_name=buyer_contact_data.get("first_name"),
                    last_name=buyer_contact_data.get("last_name"),
                    defaults={
                        "sudo_name": buyer_contact_data.get("sudo_name"),
                        "company_name": buyer_contact_data.get("company_name"),
                        "phone_number": buyer_contact_data.get("phone"),
                    }
            )
                # buyer_contact.full_clean()  # not needed for update and create
                
                # 5. Create billing address 
                billing_address_data = data["billingAddress"].copy()
                billing_address_data["contact"] = buyer_contact
                billing_address, _ = Address.objects.update_or_create(
                    contact = buyer_contact,
                    defaults = {
                        "address_line_1": billing_address_data.get("address_line_1"),
                        "address_line_2": billing_address_data.get("address_line_2"),
                        "city": billing_address_data.get("city"),
                        "state_province": billing_address_data.get("state_province"),
                        "postal_code": billing_address_data.get("postal_code"),
                        "country": billing_address_data.get("country")
                    }
                )
                
                # 6. Create buyer
                buyer, _ = Buyer.objects.update_or_create(
                    contact=buyer_contact,
                    defaults={}
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
                order, _ = Order.objects.update_or_create(
                    reference_number=reference_number,
                    defaults={
                        "buyer": buyer,
                        "status": Order.OrderStatus.PENDING,
                        "subtotal": subtotal,
                        "currency": "usd",
                    }
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
                    order_item, _ = OrderItem.objects.update_or_create(
                        order=order,
                        object_id=track_license_option.track_license_option_id,
                        defaults={
                            "content_type": content_type,
                            "quantity": quantity,
                            "price": price
                        }
                    )

                    # Create license - And MAKE SURE YO INCLUDE THE LICENSE_AGREEMENT_FILE LATER
                    license_obj, _ = License.objects.update_or_create(
                        track_license_option=track_license_option,
                        order_item=order_item,
                        defaults={
                            "created_date": timezone.now(),
                        }
                    )
                    print(f"License obj created: {license_obj}") 
                    #TODO: Automate expiration date
                    
                    # ****LICENSEHOLDING****
                    # Create license holdings for each licensee
                    # Create license holding
                    holding, _ = LicenseHolding.objects.update_or_create(
                        license=license_obj,
                        licensee=licensee,
                        defaults={}
                    )

                    # Create license status- BUT IT'S NOT ACTIVE UNTIL PAYMENT IS PROCESSED
                    license_status, _ = LicenseStatus.objects.update_or_create(
                        license=license_obj,
                        defaults={
                            "license_status_option":"Pending",
                            "license_status_date": timezone.now(),
                        }
                    )
                    
                    created_licenses.append({
                        "license_id": str(license_obj.license_id),
                        "track_id": str(track.track_id),
                        "track_title": track.title,
                        "license_type": track_license_option.license_type.license_type_name,
                        "status": "Pending Payment",
                    })
                    
                holdings.append({
                    # "licensee_id": str(licensee.licensee_id), -  prob not safe to include
                    "licensee_name": f"{licensee.music_professional.contact.first_name} {licensee.music_professional.contact.last_name}".strip(),
                    "licensee_email": licensee.music_professional.contact.email,
                    # "transaction_id": str(order.order_id), - prob not safe to include
                    "reference_number": order.reference_number ,
                    # "created_date": order.created_date, - incongruent...that would be for license
                    # "buyer_id": str(buyer.buyer_id), - not safe or needed
                    # "buyer_name": f"{buyer.contact.first_name} {buyer.contact.last_name}".strip(),
                    # "buyer_email": buyer.contact.email, - not needed as the stripe and paypal are taking care of it
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
                    "created_date": order.created_date,
                    # "buyer": { uncessary to include since stripe and paypal take care of it
                    #     "buyer_id": str(buyer.buyer_id),
                    #     "buyer_name": f"{buyer.contact.first_name} {buyer.contact.last_name}".strip(),
                    #     "buyer_email": buyer.contact.email
                    # },
                    "license_holdings": holdings,

                    "message": "Order created successfully. Payment processing required before download access."
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
    
    #This route gets the licenses and track zip files for the front end on order confirmation
    @action(detail=True, methods=['get'])
    def get_licenses_and_tracks(self, request, reference_number=None):
        """
        Get licenses and tracks for an order - only available after payment is completed.
        Treat your get_licenses 403 (“Payment not completed…”) as “not ready yet”
        Show a “Finalizing your order…” state
        Poll every ~1-2 seconds for a short period (or poll an order status endpoint), until it becomes COMPLETED and returns licenses
        """
        try:
            order = Order.objects.get(reference_number=reference_number)
            print(f"PROVIDER PAYMENT ID from PAYMENT FOR ORDER for License: {order.payments.first().provider_payment_id}")
            print(f"ORDER STATUS IN GETLICENSE: {order.status}")
            # Security check: only allow access if payment is completed
            if order.status != Order.OrderStatus.COMPLETED:
                print(f"Payment not completed. Licenses not available yet. Order status: {order.status}")
                return Response(
                    {"error": "Payment not completed. Licenses not available yet."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get all licenses for this order
            licenses = []
            for order_item in order.order_items.all():
                for license_obj in order_item.licenses.all():
                    # Only include download_url if license status is Active
                    download_url = None
                    if hasattr(license_obj, 'license_status') and license_obj.license_status.filter(license_status_option='Active').exists():
                        # license_download_url = license_obj.license_agreement_file.url if license_obj.license_agreement_file else None,
                        # track_download_url= license_obj.track_license_option.track_storage_file.file_path.url,
                        track_description = license_obj.track_license_option.track_storage_file.description,
                        track_file_format = license_obj.track_license_option.track_storage_file.file_format.name,
                        ld = get_or_create_license_zip(license_obj)  # 96h TTL
                        zip_path = reverse("download-assets", args=[license_obj.license_id, ld.token])
                        zip_url = request.build_absolute_uri(zip_path) #This is important to create a short lived url
                    licenses.append({
                        "license_id": str(license_obj.license_id),
                        "track_id": str(license_obj.track_license_option.track.track_id),
                        "track_title": license_obj.track_license_option.track.title,
                        "license_type": license_obj.track_license_option.license_type.license_type_name,
                        "status": "Active",  # We know it's active because of the check above
                        "created_date": license_obj.created_date,
                        "track_description": track_description,
                        "track_file_format": track_file_format,
                        "zip_download_url": zip_url,
                    })

            return Response({
                "order_reference_number": str(order.reference_number),
                "status": order.status,
                "licenses": licenses
            })
        
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
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
        reference_number = request.headers.get('Idempotency-Key') # different reference number for payment as oppose to order
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
                    #IMPORTANT: after webhook is excuted, stripe_intent_id comes back as field "id". So search as field "id"in payment
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

                # Make the license statuses of all the licenses active
                for order_item in order.order_items.all():
                    for license_obj in order_item.licenses.all():
                        updated = license_obj.license_status.filter(
                        license_status_option='Pending'
                        ).update(
                        license_status_option='Active',
                        license_status_date=timezone.now()
                        )
                        if updated == 0 and not license_obj.license_status.filter(license_status_option='Active').exists():
                            license_obj.license_status.create(license_status_option='Active')
                
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
            print(f"PAYMENT INTENT DATA ID: {payment_intent_data['id']}")
            try:
                payment = Payment.objects.get(
                    provider='stripe',
                    provider_payment_id=payment_intent_data['id']
                )
                
                with transaction.atomic():
                    payment.status = PaymentStatus.SUCCESS
                    payment.save()
                    print(f"Payment PROVIDER PAYMENT ID: {payment.provider_payment_id}")

                    order = payment.order
                    order.status = Order.OrderStatus.COMPLETED
                    order.save()
                    print(f"Order status updated to COMPLETED: {order.status}")

                    for order_item in order.order_items.all():
                        for license_obj in order_item.licenses.all():
                            updated = license_obj.license_status.filter(
                            license_status_option='Pending'
                            ).update(
                            license_status_option='Active',
                            license_status_date=timezone.now()
                            )
                            if updated == 0 and not license_obj.license_status.filter(license_status_option='Active').exists():
                                license_obj.license_status.create(license_status_option='Active')
                
                    
                    #******* Fulfill STRIPE order licenses after transaction commits asynchronously using Celery    
                    # transaction.on_commit(lambda: __import__("licenses.tasks").tasks.fulfill_order_licenses.delay(str(order.order_id)))
                    transaction.on_commit(lambda: fulfill_order_licenses.delay(str(order.order_id)))

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