# server/app/services/email.py
from __future__ import annotations

import os
import json
from email.message import EmailMessage
import smtplib

from fastapi import HTTPException

from app.schemas.quote import SendOfferRequest, EstimateResponse


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

EMAIL_TO = os.getenv("EMAIL_TO")  # your inbox
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER or "")


def _require_email_config() -> None:
    missing = []
    for key, val in [
        ("SMTP_HOST", SMTP_HOST),
        ("SMTP_USER", SMTP_USER),
        ("SMTP_PASS", SMTP_PASS),
        ("EMAIL_TO", EMAIL_TO),
        ("EMAIL_FROM", EMAIL_FROM),
    ]:
        if not val:
            missing.append(key)

    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Email not configured. Missing: {', '.join(missing)}",
        )


def _format_offer_email(payload: SendOfferRequest, estimate: EstimateResponse) -> str:
    lines = [
        "New Grillz Offer",
        "",
        f"Customer email: {payload.email}",
        f"Name: {payload.name or '-'}",
        f"Instagram: {payload.instagram or '-'}",
        "",
        f"Arch: {payload.estimate.arch}",
        f"Metal: {payload.estimate.metal_type}",
        f"Selected teeth ({len(payload.estimate.selected_teeth)}): {', '.join(payload.estimate.selected_teeth)}",
        "",
        "Per-tooth requests:",
    ]

    if not payload.estimate.per_tooth:
        lines.append("  - None")
    else:
        for t in payload.estimate.per_tooth:
            addons = ", ".join(t.addons) if t.addons else "-"
            note = t.note or "-"
            lines.append(f"  - {t.tooth_id}: addons={addons} | note={note}")

    lines += [
        "",
        "Estimate breakdown:",
    ]
    for item in estimate.breakdown:
        lines.append(f"  - {item.label}: {estimate.currency} {item.amount:.2f}")

    lines += [
        "",
        f"TOTAL ESTIMATE: {estimate.currency} {estimate.total:.2f}",
        "",
        f"Disclaimer: {estimate.disclaimer}",
        "",
        "Client notes:",
        payload.client_notes or "-",
        "",
        "Raw payload (JSON):",
        json.dumps(payload.model_dump(), indent=2),
    ]

    return "\n".join(lines)


async def send_offer_email(payload: SendOfferRequest, estimate: EstimateResponse) -> None:
    """
    Sends the offer to your email via SMTP. Keep this as an integration layer.
    """
    _require_email_config()

    subject = f"Grillz Offer ({len(payload.estimate.selected_teeth)} teeth, {payload.estimate.metal_type})"
    body = _format_offer_email(payload, estimate)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=12) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to send email: {e}") from e

