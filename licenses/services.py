
from django.template import Template, Context
from django.core.files.base import ContentFile
# from weasyprint import HTML
from django.urls import reverse
from django.core.mail import send_mail
from .models import License, LicenseHolding
from django.core.mail import EmailMessage
from django.conf import settings
import io
try:
    from weasyprint import HTML
except OSError:
    HTML = None


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
        "licensee_address": licensee.music_professional.contact.address,
        "licensor_name": licensor.contact.first_name + " " + licensor.contact.last_name,
        "licensor_address": licensor.contact.address,
        "track_title": track.title,
        "track_duration": track.duration_seconds,
        "writers": [
            f"{contrib.music_professional.contact.first_name} "
            f"{contrib.music_professional.contact.last_name}"
            f"{contrib.music_professional.contact.sudo_name}"
            for contrib in license_obj.track_license_option.track.contributors.all()
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
def render_license_agreement_html(template_text, context):
    t = Template(template_text)
    return t.render(Context(context))

# generate the license pdf with the license rendered above
def generate_license_agreement_pdf(license_obj, html): #I included the license_obj in order to save the generated pdf in it
    pdf_io = io.BytesIO()
    HTML(string=html).write_pdf(pdf_io)
    pdf_io.seek(0)
    filename = f"license_{license_obj.license_id}.pdf"
    license_obj.license_agreement_file.save(filename, ContentFile(pdf_io.read()))
    license_obj.save()

# higher level function to generate the license pdf with the license rendered above (uses the 2 functions above)
def generate_license_agreement(license_obj):
    if HTML is None:
        # raise Exception("WeasyPrint is not installed. Please install it to generate license agreements.")
        return
    license_type = license_obj.track_license_option.license_type
    context = build_context_for_license(license_obj)
    html = render_license_agreement_html(template_text, context)
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
# TODO send email with download url 
def send_license_email(
    license_obj: License,
    to_email: str, 
    license_url: str,
    track_url: str,
) -> None:
    """
    Send an email to the buyer with the license PDF attached
    and links to download the track and license.
    """
    track_title = license_obj.track_license_option.track.title

    subject = f"Your License for {track_title}"

    body = (
        "Thank you for your purchase.\n\n"
        f"You can download your track here:\n{track_url}\n\n"
        f"You can download your license agreement here:\n{license_url}\n\n"
        "We've also attached a PDF copy of your license agreement to this email."
    )

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,  # uses DEFAULT_FROM_EMAIL
        to=[to_email],
    )

    if license_obj.license_agreement_file:
        license_obj.license_agreement_file.open("rb")
        pdf_content = license_obj.license_agreement_file.read()
        license_obj.license_agreement_file.close()

        filename = license_obj.license_agreement_file.name.split("/")[-1] or "license.pdf"
        email.attach(filename, pdf_content, "application/pdf")
    try:
        email.send(fail_silently=False)
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        raise