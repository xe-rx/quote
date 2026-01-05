# server/app/services/pricing.py
from __future__ import annotations

import os
from typing import Dict, List

from app.schemas.quote import EstimateRequest, EstimateResponse, LineItem


# ---- Pricing knobs (env-configurable) ----
CURRENCY = os.getenv("CURRENCY", "USD")

BASE_PRICE_PER_TOOTH = float(os.getenv("BASE_PRICE_PER_TOOTH", "50"))
ARCH_FEE_UPPER = float(os.getenv("ARCH_FEE_UPPER", "0"))
ARCH_FEE_LOWER = float(os.getenv("ARCH_FEE_LOWER", "0"))

# NOTE: ensure this matches frontend, not dynamic at the moment.
ADDON_PRICES: Dict[str, float] = {
    "open_face": float(os.getenv("ADDON_OPEN_FACE", "20")),
    "heart": float(os.getenv("ADDON_HEART", "20")),
    "bar": float(os.getenv("ADDON_BAR", "0")),
}

DISCLAIMER = os.getenv(
    "DISCLAIMER",
    "Estimate only. Final details and pricing are confirmed after review.",
)


def _arch_fee(arch: str) -> float:
    if arch == "upper":
        return ARCH_FEE_UPPER
    if arch == "lower":
        return ARCH_FEE_LOWER
    # both
    return ARCH_FEE_UPPER + ARCH_FEE_LOWER


def _addons_total(req: EstimateRequest) -> float:
    total = 0.0
    for tooth in req.per_tooth:
        for addon in tooth.addons:
            total += float(ADDON_PRICES.get(addon, 0.0))
    return total


async def calculate_estimate(req: EstimateRequest) -> EstimateResponse:
    """
    Calculates an estimated price based on:
    - base per-tooth
    - optional arch fee
    - per-tooth add-ons
    (Silver spot API can be added later without changing the endpoint signature.)
    """
    tooth_count = len(req.selected_teeth)
    breakdown: List[LineItem] = []

    base = BASE_PRICE_PER_TOOTH * tooth_count
    breakdown.append(LineItem(label=f"Base ({tooth_count} teeth)", amount=round(base, 2)))

    arch_fee = _arch_fee(req.arch)
    if arch_fee:
        breakdown.append(LineItem(label=f"Arch fee ({req.arch})", amount=round(arch_fee, 2)))

    addons = _addons_total(req)
    if addons:
        breakdown.append(LineItem(label="Add-ons", amount=round(addons, 2)))

    total = round(sum(item.amount for item in breakdown), 2)

    return EstimateResponse(
        currency=CURRENCY,
        total=total,
        breakdown=breakdown,
        disclaimer=DISCLAIMER,
    )
