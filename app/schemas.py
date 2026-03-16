"""Pydantic request/response schemas for the admin API."""
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Customers ─────────────────────────────────────────────────────────────────

class CustomerCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    twilio_number: str = Field(..., min_length=8, max_length=20)
    plumber_phone: str = Field(..., min_length=8, max_length=20)
    calendly_url: str = Field(..., max_length=500)
    greeting_message: Optional[str] = Field(None, description="Custom greeting SMS. Defaults to company_name-based greeting.")
    sms_provider: Literal["twilio", "46elks"] = "twilio"


class CustomerPatch(BaseModel):
    """All fields optional — only supplied fields are updated."""
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    twilio_number: Optional[str] = Field(None, min_length=8, max_length=20)
    plumber_phone: Optional[str] = Field(None, min_length=8, max_length=20)
    calendly_url: Optional[str] = Field(None, max_length=500)
    greeting_message: Optional[str] = Field(None, description="Set to null to revert to default greeting.")
    is_active: Optional[bool] = None
    sms_provider: Optional[Literal["twilio", "46elks"]] = None


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    twilio_number: str
    plumber_phone: str
    calendly_url: str
    greeting_message: Optional[str]
    sms_provider: str
    is_active: bool
    created_at: datetime


class CustomerStats(BaseModel):
    total_conversations: int
    conversations_last_7_days: int
    urgent_alerts_sent: int


class CustomerWithStats(CustomerOut):
    stats: CustomerStats


# ── Conversations ─────────────────────────────────────────────────────────────

class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    caller_phone: str
    current_step: str
    problem_description: Optional[str]
    address: Optional[str]
    urgency: Optional[str]
    created_at: datetime
    updated_at: datetime


# ── Messages ──────────────────────────────────────────────────────────────────

class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    direction: str
    body: str
    created_at: datetime
