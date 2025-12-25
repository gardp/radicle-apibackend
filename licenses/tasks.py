from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from licenses.models import License
from licenses.services import (
    generate_license_agreement,
    build_download_urls_from_base,
    send_license_email,
)

# ----------------CELERY TASKS----------------
# One email per order
# Attach all PDFs available
# Idempotent: if already emailed, skip
# Race-safe: select_for_update() prevents double-sends in Postgres
# Retries: 5 retries with exponential backoff/jitter for transient failures (SMTP/network)
# CREATE CELERY TASK: ONE TASK PER ORDER TO FULFILL TASKS
@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def fulfill_order_licenses(self, order_id: str) -> dict:
    """
    One task per order:
    - generate PDFs (best effort) for all licenses in order
    - send one aggregated email to the licensee
    - mark all licenses as emailed (license_email_sent_at)
    """
    with transaction.atomic():
        # Lock all licenses for this order to avoid double-send
        licenses = list(
            License.objects
            .select_for_update()
            .select_related("track_license_option__track", "order_item__order")
            .filter(order_item__order_id=order_id)
            .order_by("created_date")
        )

        if not licenses:
            return {"status": "no_licenses", "order_id": order_id}

        # If everything already emailed, do nothing (idempotency)
        if all(l.license_email_sent_at is not None for l in licenses):
            return {"status": "already_emailed", "order_id": order_id, "count": len(licenses)}

        # Determine licensee email (default: first license holding's licensee)
        first = licenses[0]
        holding = first.license_holdings.first()
        if not holding or not holding.licensee or not holding.licensee.music_professional:
            # This is a "data problem" not a retryable transient error.
            # You could raise a custom exception and exclude it from autoretry.
            return {"status": "missing_licensee_email", "order_id": order_id}

        to_email = holding.licensee.music_professional.contact.email
        if not to_email:
            return {"status": "missing_licensee_email", "order_id": order_id}

        order_reference = first.order_item.order.reference_number

        items = []
        attachments = []
        # items is a list of dicts: {track_title, track_url, license_url}
        # attachments is a list of (filename, bytes, mimetype) for PDFs that exist

        # Generate PDFs + build links + gather attachments
        for lic in licenses:
            if not lic.license_agreement_file:
                # best effort; no-op if WeasyPrint not available
                generate_license_agreement(lic)

            license_url, track_url = build_download_urls_from_base(settings.PUBLIC_BASE_URL, lic)
            items.append({
                "track_title": lic.track_license_option.track.title,
                "track_url": track_url,
                "license_url": license_url,
            })

            if lic.license_agreement_file:
                lic.license_agreement_file.open("rb")
                content = lic.license_agreement_file.read()
                lic.license_agreement_file.close()

                filename = lic.license_agreement_file.name.split("/")[-1] or f"license_{lic.license_id}.pdf"
                attachments.append((filename, content, "application/pdf"))

        # Send one email
        send_license_email(
            to_email=to_email,
            order_reference=order_reference,
            licenses=licenses,
        )

        # Mark as emailed (only after successful send)
        now = timezone.now()
        for lic in licenses:
            if lic.license_email_sent_at is None:
                lic.license_email_sent_at = now
                lic.save(update_fields=["license_email_sent_at"])

        return {"status": "sent", "order_id": order_id, "count": len(licenses), "to_email": to_email}