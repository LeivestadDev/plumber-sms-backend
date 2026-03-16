from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.conversation import create_conversation, get_active_conversation, handle_message
from app.database import AsyncSessionLocal, get_db, init_db
from app.models import Customer
from app.providers import get_provider
from app.providers.base import IncomingSMS, SMSProvider
from app.providers.fortysix_elks import FortysixElksProvider
from app.providers.twilio_provider import TwilioProvider
from app.reminders import reminder_worker
from app.routers import conversations as conv_router
from app.routers import customers as cust_router

logger = logging.getLogger(__name__)


async def seed_from_env_if_empty(db: AsyncSession) -> None:
    """If the customers table is empty and env vars are configured, create a default customer.

    This preserves backward compatibility when upgrading from the single-tenant version.
    """
    twilio_number = os.getenv("TWILIO_NUMBER")
    plumber_phone = os.getenv("PLUMBER_PHONE")
    if not twilio_number or not plumber_phone:
        return

    result = await db.execute(select(Customer).limit(1))
    if result.scalar_one_or_none() is not None:
        return  # DB already has customers

    customer = Customer(
        company_name="Default",
        twilio_number=twilio_number,
        plumber_phone=plumber_phone,
        calendly_url=os.getenv(
            "CALENDLY_URL",
            "https://calendly.com/svardirekte/befaring-rorleggerhjelp",
        ),
    )
    db.add(customer)
    await db.commit()
    logger.warning(
        "Auto-seeded default customer from env vars (twilio_number=%s). "
        "Run scripts/seed_db.py to manage customers explicitly.",
        twilio_number,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with AsyncSessionLocal() as db:
        await seed_from_env_if_empty(db)
    task = asyncio.create_task(reminder_worker())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="SvarDirekte API",
    description=(
        "SMS automation backend for trades businesses (rørleggere m.fl.).\n\n"
        "**Webhooks**: `POST /webhook/twilio` and `POST /webhook/46elks`.\n\n"
        "**Admin API**: `/api/*` endpoints require the `X-API-Key` header."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(cust_router.router)
app.include_router(conv_router.router)


async def _get_customer_for_number(
    db: AsyncSession, phone_number: str
) -> Customer | None:
    result = await db.execute(
        select(Customer).where(
            Customer.twilio_number == phone_number,
            Customer.is_active == True,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()


async def _process_incoming(
    db: AsyncSession, incoming: IncomingSMS, provider: SMSProvider
) -> dict:
    """Shared logic for all SMS webhook endpoints."""
    customer = await _get_customer_for_number(db, incoming.to_number)
    if not customer:
        logger.warning("Incoming SMS to unregistered number: %s", incoming.to_number)
        if incoming.to_number and incoming.from_number:
            await provider.send_sms(
                to=incoming.from_number,
                from_=incoming.to_number,
                body="Vi kunne ikke behandle henvendelsen din. Vennligst kontakt oss direkte.",
            )
        return {"status": "unknown_number"}

    conversation = await get_active_conversation(db, customer.id, incoming.from_number)
    if conversation is None:
        await create_conversation(db, customer, incoming.from_number, provider)
        await db.commit()
        return {"status": "ok"}

    await handle_message(db, customer, conversation, incoming.body, provider)
    return {"status": "ok"}


@app.post("/webhook/twilio")
async def webhook_twilio(request: Request, db: AsyncSession = Depends(get_db)):
    form = await request.form()
    provider = TwilioProvider()
    incoming = provider.parse_incoming(dict(form))
    if not incoming.from_number or not incoming.body:
        return {"status": "ignored"}
    return await _process_incoming(db, incoming, provider)


@app.post("/webhook/46elks")
async def webhook_46elks(request: Request, db: AsyncSession = Depends(get_db)):
    form = await request.form()
    provider = FortysixElksProvider()
    incoming = provider.parse_incoming(dict(form))
    if not incoming.from_number or not incoming.body:
        return {"status": "ignored"}
    return await _process_incoming(db, incoming, provider)


@app.post("/incoming-sms")
async def incoming_sms(request: Request, db: AsyncSession = Depends(get_db)):
    """Backward-compatible alias for /webhook/twilio."""
    return await webhook_twilio(request, db)
