from django.template import Template, Context
from django.core.files.base import ContentFile
from xhtml2pdf import pisa
from django.urls import reverse
from urllib.parse import urljoin
from django.conf import settings
from django.core.mail import EmailMessage
from .models import License, LicenseHolding, LicenseDownload
from django.core.files.storage import default_storage
from music.models import TrackStorageFile
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

    # License PDF (unchanged)
    license_path = reverse("download-license", args=[license_id])
    license_url = urljoin(base_url.rstrip("/") + "/", license_path.lstrip("/"))

    # Assets ZIP (single file or stems) via tokenized URL
    ld = get_or_create_license_zip(license_obj)  # ensures ZIP exists and 72h token is set
    asset_path = reverse("download-assets", args=[license_id, ld.token])
    asset_url = urljoin(base_url.rstrip("/") + "/", asset_path.lstrip("/"))

    # Keep return signature the same
    return license_url, asset_url


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
    
    # Prepare context for template
    license_items = []
    attachments = []
    
    for license in licenses:
        if license.license_agreement_file:
            license_url, track_url = build_download_urls_from_base(settings.PUBLIC_BASE_URL, license)
            
            license_items.append({
                'track_title': license.track_license_option.track.title,
                'track_url': track_url,
                'license_url': license_url
            })
            
            # Prepare attachment
            license.license_agreement_file.open("rb")
            content = license.license_agreement_file.read()
            license.license_agreement_file.close()
            filename = license.license_agreement_file.name.split("/")[-1] or f"license_{license.license_id}.pdf"
            attachments.append((filename, content, "application/pdf"))

    # Send via EmailService
    from core.email_service import EmailService
    
    EmailService.send_transactional_email(
        subject=f"Tracks and Licenses for Order {order_reference}",
        recipient_list=[to_email],
        template_name="emails/license_email",
        context={
            'order_reference': order_reference,
            'licenses': license_items
        },
        attachments=attachments,
        reply_to=[settings.DEFAULT_FROM_EMAIL]
    )

# get or generate a track zip file for either single tracks or stems that will be sent to user via email or on the website
def get_or_create_license_zip(license_obj):
    from django.core.files.base import File
    from django.core.files.storage import default_storage
    from django.utils import timezone
    from django.utils.text import slugify
    import secrets, zipfile, os, tempfile

    existing = getattr(license_obj, "license_download", None)
    if existing and existing.expires_at > timezone.now() and existing.zip_file:
        return existing

    track = license_obj.track_license_option.track
    tsf = license_obj.track_license_option.track_storage_file
    fmt = tsf.file_format.name

    if fmt == "Stems":
        files_qs = TrackStorageFile.objects.filter(
            track_license_options__track=track,
            file_format__name="Stems",
        ).distinct()
        files = [(f.file_path.name, os.path.basename(f.file_path.name)) for f in files_qs]
        label = "stems"
    else:
        files = [(tsf.file_path.name, os.path.basename(tsf.file_path.name))]
        label = fmt.lower()
    # add license agreement to zip if it exists
    if license_obj.license_agreement_file:
        files.append((license_obj.license_agreement_file.name, "LICENSE.pdf"))
    title = getattr(track, "title", str(track.track_id))
    zip_name = f"{slugify(title)}_{label}_{license_obj.license_id}.zip"
    storage_path = f"license_zips/{zip_name}"

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for storage_key, arcname in files:
                with default_storage.open(storage_key, "rb") as f:
                    zf.writestr(arcname, f.read())
        with open(tmp_path, "rb") as f:
            saved_name = default_storage.save(storage_path, File(f))
    finally:
        os.remove(tmp_path)

    token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timezone.timedelta(hours=settings.LICENSE_ZIP_TTL_HOURS)

    obj, _ = LicenseDownload.objects.update_or_create(
        license=license_obj,
        defaults={"zip_file": saved_name, "token": token, "expires_at": expires_at},
    )
    return obj










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


