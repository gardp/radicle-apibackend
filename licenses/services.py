
from django.template import Template, Context
from django.core.files.base import ContentFile
from xhtml2pdf import pisa
from django.urls import reverse
from urllib.parse import urljoin
from django.core.mail import send_mail
from .models import License, LicenseHolding
from django.core.mail import EmailMessage
from django.conf import settings
import io
# try:
#     from weasyprint import HTML
# except (OSError, ImportError, ModuleNotFoundError):
#     HTML = None


def build_context_for_license(license_obj: License) -> dict:
    """
    Build the context dict used to render the license contract template.
    """
    # Get the main license holding (assuming one primary)
    license_holding = (
        LicenseHolding.objects
        .select_related('licensee__music_professional')
        .filter(license=license_obj)
        .first()
    )
    
    # track = 
    if license_holding and license_holding.licensee:
        licensee = license_holding.licensee
        track_license_option = license_obj.track_license_option
        license_type = track_license_option.license_type
        track = track_license_option.track
        licensor = track.contributions.first().contributor.music_professional
        licensee_template = license_type.license_template

    license_contract_context = {
        "license_type_name": license_type.license_type_name,
        "licensee_template": licensee_template,
        "licensee_name": licensee.music_professional.contact.first_name + " " + licensee.music_professional.contact.last_name,
        "licensee_address": licensee.music_professional.contact.addresses,
        "licensor_name": licensor.contact.first_name + " " + licensor.contact.last_name,
        "licensor_address": licensor.contact.addresses,
        "track_title": track.title,
        "track_duration": track.duration_seconds,
        "writers": [
            f"{contrib.contributor.music_professional.contact.first_name} "
            f"{contrib.contributor.music_professional.contact.last_name}"
            f"{contrib.contributor.music_professional.contact.sudo_name}"
            for contrib in license_obj.track_license_option.track.contributions.all()
        ],
        "effective_date": license_obj.created_date,
        "term": license_type.license_term,
        "price": license_type.price,
        "currency": license_type.currency,
        "download_limit": license_type.download_limit,
        "streaming_limit": license_type.streaming_limit,
        "monetized_radio_plays": license_type.monetized_radio_plays,
        "video_rights": license_type.video_rights,
        "royalty_payment": license_type.royalty_payment,
        "credit_requirement": license_type.credit_requirement,
        "licensee_share": license_holding.licensee_split,
        "licensee_pro_affiliation": license_holding.licensee.music_professional.pro_affiliation, 
    }
    return license_contract_context


# render the complete license contract with the inserted context data above
def render_license_agreement_html(template_text, context): # template text is the license_template in the license_type
    t = Template(template_text)
    return t.render(Context(context))

# generate the license pdf with the license rendered above
def generate_license_agreement_pdf(license_obj, html): #I included the license_obj in order to save the generated pdf in it
    pdf_io = io.BytesIO()
    pisa.CreatePDF(html, dest=pdf_io)
    pdf_io.seek(0)
    filename = f"license_{license_obj.license_id}.pdf"
    license_obj.license_agreement_file.save(filename, ContentFile(pdf_io.read()))
    license_obj.save()

# higher level function to generate the license pdf with the license rendered above (uses the 2 functions above)
def generate_license_agreement(license_obj):
    if pisa is None:
        return # raise Exception("Pisa is not installed. Please install it to generate license agreements.")
    license_type = license_obj.track_license_option.license_type
    context = build_context_for_license(license_obj)
    html = render_license_agreement_html(license_type.license_template, context)
    generate_license_agreement_pdf(license_obj, html) #adding it to the database

# TODO create and attach PDF license agreement 
# TODO Build download url
def build_download_urls(request, license_obj: License) -> tuple[str, str]:
    """
    Build absolute URLs for downloading the license PDF and track file.
    """
    license_id = str(license_obj.license_id)

    license_path = reverse("download-license", args=[license_id])
    track_path = reverse("download-track", args=[license_id])

    license_url = request.build_absolute_uri(license_path)
    track_url = request.build_absolute_uri(track_path)
    print(f"track_url: {track_url}, license_url: {license_url}")

    return license_url, track_url

# ----------------FUNCTIONS EXCLUSIVE FOR CELERY----------------
# Add URL building that works in Celery (no request)
def build_download_urls_from_base(base_url: str, license_obj: License) -> tuple[str, str]:
    license_id = str(license_obj.license_id)
    license_path = reverse("download-license", args=[license_id])
    track_path = reverse("download-track", args=[license_id])
    license_url = urljoin(base_url.rstrip("/") + "/", license_path.lstrip("/"))
    track_url = urljoin(base_url.rstrip("/") + "/", track_path.lstrip("/"))
    return license_url, track_url

# Send an email to the buyer with the license PDF attached and links to download the track and license with celery
# TODO send email with download url 
def send_license_email(
    to_email: str, 
    order_reference: str,
    licenses: list[License],
) -> None:
    """
    Send an email to the buyer with the license PDF attached
    and links to download the track and license.
    """
    print("SENDING EMAIL TO", to_email)
    track_license_urls = []
    subject = f"Tracks and Licenses for Order {order_reference}"
    attachments = []
    for license in licenses:
        if license.license_agreement_file:
            license_url, track_url = build_download_urls_from_base(settings.PUBLIC_BASE_URL, license) # because celery doesn't allow request object
            track_license_urls.append(
                f"Your track and license for track:{license.track_license_option.track.title}\n\n"
                f"Download your track here:\n{track_url}\n\n"
                f"Download a copy of your license agreement here:\n{license_url}\n\n\n"
            )
            
            license.license_agreement_file.open("rb")
            content = license.license_agreement_file.read()
            license.license_agreement_file.close()
            filename = license.license_agreement_file.name.split("/")[-1] or f"license_{license.license_id}.pdf"
            attachments.append((filename, content, "application/pdf"))

    
    body = (
        "Thank you for your purchase.\n\n"
        f"Order Reference: {order_reference}\n\n"
        f"{track_license_urls}\n\n"
    )
    
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,  # uses DEFAULT_FROM_EMAIL
        to=[to_email],
    )

    if attachments:
        for filename, content, mimetype in attachments:
            email.attach(filename, content, mimetype)
    # email.send(fail_silently=False)
    try:
        email.send(fail_silently=False)
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        raise


# THIS IS UNECESSARY FOR NOW AS PAYPAL AND STRIPE AS A DEFAULT PAYMENT EMAIL TO SEND RECEIPT
# def send_order_license_email(
#     *,
#     to_email: str,
#     order_reference: str,
#     items: list[dict],
#     attachments: list[tuple[str, bytes, str]],
# ) -> None:
#     subject = f"Your Licenses for Order {order_reference}"
#     lines = [
#         "Thank you for your purchase.",
#         "",
#         f"Order Reference: {order_reference}",
#         "",
#         "Your items:",
#         "",
#     ]
#     for item in items:
#         lines.append(f"- Track: {item['track_title']}")
#         lines.append(f"  Track download: {item['track_url']}")
#         lines.append(f"  License download: {item['license_url']}")
#         lines.append("")
#     body = "\n".join(lines)
#     email = EmailMessage(
#         subject=subject,
#         body=body,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=[to_email],
#     )
#     for filename, content, mimetype in attachments:
#         email.attach(filename, content, mimetype)
#     email.send(fail_silently=False)

# TODO send email with download url 
# def send_license_email(
#     license_obj: License,
#     to_email: str, 
#     license_url: str,
#     track_url: str,
# ) -> None:
#     """
#     Send an email to the buyer with the license PDF attached
#     and links to download the track and license.
#     """
#     track_title = license_obj.track_license_option.track.title

#     subject = f"Your License for {track_title}"

#     body = (
#         "Thank you for your purchase.\n\n"
#         f"You can download your track here:\n{track_url}\n\n"
#         f"You can download your license agreement here:\n{license_url}\n\n"
#         "We've also attached a PDF copy of your license agreement to this email."
#     )

#     email = EmailMessage(
#         subject=subject,
#         body=body,
#         from_email=settings.DEFAULT_FROM_EMAIL,  # uses DEFAULT_FROM_EMAIL
#         to=[to_email],
#     )

#     if license_obj.license_agreement_file:
#         license_obj.license_agreement_file.open("rb")
#         pdf_content = license_obj.license_agreement_file.read()
#         license_obj.license_agreement_file.close()

#         filename = license_obj.license_agreement_file.name.split("/")[-1] or "license.pdf"
#         email.attach(filename, pdf_content, "application/pdf")
#     try:
#         email.send(fail_silently=False)
#     except Exception as e:
#         print(f"Failed to send email: {str(e)}")
#         raise


