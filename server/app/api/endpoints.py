# server/app/api/endpoints.py
from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, HTTPException

from app.schemas.quote import EstimateRequest, EstimateResponse, SendOfferRequest, SendOfferResponse
from app.services.pricing import calculate_estimate
from app.services.email import send_offer_email

router = APIRouter()


@router.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@router.post("/estimate", response_model=EstimateResponse)
async def estimate(req: EstimateRequest) -> EstimateResponse:
    """
    Returns an estimated price + breakdown for the quote configuration.
    Business logic lives in app.services.pricing.
    """
    # Small HTTP-layer validation that depends on request structure
    selected = set(req.selected_teeth)
    for t in req.per_tooth:
        if t.tooth_id not in selected:
            raise HTTPException(
                status_code=400,
                detail=f"per_tooth tooth_id '{t.tooth_id}' is not in selected_teeth",
            )

    return await calculate_estimate(req)


@router.post("/send-offer", response_model=SendOfferResponse)
async def send_offer(payload: SendOfferRequest) -> SendOfferResponse:
    """
    Emails the offer to you (and optionally a receipt to the customer).
    Integrations live in app.services.email.
    """
    # Always recompute estimate server-side (prevents client tampering).
    estimate_resp = await calculate_estimate(payload.estimate)

    await send_offer_email(payload=payload, estimate=estimate_resp)
    return SendOfferResponse(ok=True)
