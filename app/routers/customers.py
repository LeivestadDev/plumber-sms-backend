"""Admin endpoints for managing customers and browsing their conversations."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_api_key
from app.database import get_db
from app.models import Conversation, Customer
from app.schemas import (
    ConversationOut,
    CustomerCreate,
    CustomerOut,
    CustomerPatch,
    CustomerStats,
    CustomerWithStats,
)

router = APIRouter(
    prefix="/api/customers",
    tags=["Customers"],
    dependencies=[Depends(require_api_key)],
)


async def _get_customer_or_404(db: AsyncSession, customer_id: int) -> Customer:
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found.")
    return customer


async def _compute_stats(db: AsyncSession, customer_id: int) -> CustomerStats:
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    total = await db.scalar(
        select(func.count())
        .select_from(Conversation)
        .where(Conversation.customer_id == customer_id)
    ) or 0

    last_7 = await db.scalar(
        select(func.count())
        .select_from(Conversation)
        .where(
            Conversation.customer_id == customer_id,
            Conversation.created_at >= seven_days_ago,
        )
    ) or 0

    urgent = await db.scalar(
        select(func.count())
        .select_from(Conversation)
        .where(
            Conversation.customer_id == customer_id,
            Conversation.urgency == "akutt",
        )
    ) or 0

    return CustomerStats(
        total_conversations=total,
        conversations_last_7_days=last_7,
        urgent_alerts_sent=urgent,
    )


# ── POST /api/customers ───────────────────────────────────────────────────────

@router.post(
    "",
    response_model=CustomerOut,
    status_code=201,
    summary="Create a new customer",
)
async def create_customer(
    body: CustomerCreate,
    db: AsyncSession = Depends(get_db),
) -> Customer:
    customer = Customer(**body.model_dump())
    db.add(customer)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"twilio_number '{body.twilio_number}' is already registered.",
        )
    await db.refresh(customer)
    return customer


# ── GET /api/customers ────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=List[CustomerOut],
    summary="List all customers",
)
async def list_customers(
    active: Optional[bool] = Query(None, description="Filter by is_active status"),
    db: AsyncSession = Depends(get_db),
) -> list:
    stmt = select(Customer).order_by(Customer.id)
    if active is not None:
        stmt = stmt.where(Customer.is_active == active)  # noqa: E712
    result = await db.execute(stmt)
    return result.scalars().all()


# ── GET /api/customers/{id} ───────────────────────────────────────────────────

@router.get(
    "/{customer_id}",
    response_model=CustomerWithStats,
    summary="Get a customer with conversation statistics",
)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    customer = await _get_customer_or_404(db, customer_id)
    stats = await _compute_stats(db, customer_id)
    return {**CustomerOut.model_validate(customer).model_dump(), "stats": stats}


# ── PATCH /api/customers/{id} ─────────────────────────────────────────────────

@router.patch(
    "/{customer_id}",
    response_model=CustomerOut,
    summary="Partially update a customer",
)
async def patch_customer(
    customer_id: int,
    body: CustomerPatch,
    db: AsyncSession = Depends(get_db),
) -> Customer:
    customer = await _get_customer_or_404(db, customer_id)

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        return customer  # nothing to do

    for field, value in update_data.items():
        setattr(customer, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"twilio_number '{body.twilio_number}' is already registered.",
        )
    await db.refresh(customer)
    return customer


# ── GET /api/customers/{id}/conversations ─────────────────────────────────────

@router.get(
    "/{customer_id}/conversations",
    response_model=List[ConversationOut],
    summary="List conversations for a customer",
)
async def list_conversations(
    customer_id: int,
    status: Optional[str] = Query(
        None,
        description="Filter by status: 'active' (not done/expired), 'done', or 'expired'.",
    ),
    db: AsyncSession = Depends(get_db),
) -> list:
    await _get_customer_or_404(db, customer_id)

    stmt = (
        select(Conversation)
        .where(Conversation.customer_id == customer_id)
        .order_by(Conversation.created_at.desc())
    )

    if status == "active":
        stmt = stmt.where(~Conversation.current_step.in_(["done", "expired"]))
    elif status in ("done", "expired"):
        stmt = stmt.where(Conversation.current_step == status)
    elif status is not None:
        raise HTTPException(
            status_code=422,
            detail="status must be one of: active, done, expired.",
        )

    result = await db.execute(stmt)
    return result.scalars().all()
