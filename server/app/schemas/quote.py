# server/app/schemas/quote.py
from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


Arch = Literal["upper", "lower", "both"]
MetalType = Literal["s925"]


class PerToothRequest(BaseModel):
    tooth_id: str = Field(..., description="Stable tooth id like U1..U16, L1..L16")
    addons: List[str] = Field(
        default_factory=list, description="e.g. ['open', 'heart', 'bar']"
    )
    note: Optional[str] = Field(default=None, description="Free text per tooth")


class EstimateRequest(BaseModel):
    arch: Arch
    selected_teeth: List[str] = Field(..., min_items=1)
    metal_type: MetalType = "s925"
    per_tooth: List[PerToothRequest] = Field(default_factory=list)


class LineItem(BaseModel):
    label: str
    amount: float


class EstimateResponse(BaseModel):
    currency: str
    total: float
    breakdown: List[LineItem]
    disclaimer: str


class SendOfferRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    instagram: Optional[str] = None
    estimate: EstimateRequest
    client_notes: Optional[str] = None


class SendOfferResponse(BaseModel):
    ok: bool = True
