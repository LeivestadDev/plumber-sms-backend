from __future__ import annotations

import logging
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, Customer, Message
from app.providers.base import SMSProvider
from app.urgency import classify_urgency

logger = logging.getLogger(__name__)

CONVERSATION_TIMEOUT_HOURS = 24
MIN_PROBLEM_LENGTH = 5  # characters


async def get_active_conversation(
    db: AsyncSession,
    customer_id: int,
    caller_phone: str,
) -> Conversation | None:
    cutoff = datetime.utcnow() - timedelta(hours=CONVERSATION_TIMEOUT_HOURS)
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.customer_id == customer_id,
            Conversation.caller_phone == caller_phone,
            ~Conversation.current_step.in_(["done", "expired"]),
            Conversation.updated_at >= cutoff,
        )
        .order_by(Conversation.updated_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_conversation(
    db: AsyncSession,
    customer: Customer,
    caller_phone: str,
    provider: SMSProvider,
) -> Conversation:
    greeting = customer.greeting_message or (
        f"Hei! Du har nådd {customer.company_name}. Hva kan vi hjelpe deg med?"
    )

    conv = Conversation(
        customer_id=customer.id,
        caller_phone=caller_phone,
        current_step="problem",
    )
    db.add(conv)
    await db.flush()  # populate conv.id before adding the Message FK

    await provider.send_sms(to=caller_phone, from_=customer.twilio_number, body=greeting)
    db.add(Message(conversation_id=conv.id, direction="outbound", body=greeting))
    return conv


async def handle_message(
    db: AsyncSession,
    customer: Customer,
    conversation: Conversation,
    inbound_text: str,
    provider: SMSProvider,
) -> None:
    # Clear any pending reminder — the user has responded
    if conversation.reminder_sent_at is not None:
        conversation.reminder_sent_at = None

    db.add(
        Message(
            conversation_id=conversation.id,
            direction="inbound",
            body=inbound_text,
        )
    )

    step = conversation.current_step
    caller = conversation.caller_phone
    from_ = customer.twilio_number

    async def reply(body: str) -> None:
        await provider.send_sms(to=caller, from_=from_, body=body)
        db.add(Message(conversation_id=conversation.id, direction="outbound", body=body))

    if step == "problem":
        if len(inbound_text.strip()) < MIN_PROBLEM_LENGTH:
            await reply("Kan du beskrive problemet litt mer detaljert?")
        else:
            conversation.problem_description = inbound_text
            conversation.current_step = "address"
            await reply("Hvor gjelder dette? (adresse)")

    elif step == "address":
        conversation.address = inbound_text
        conversation.current_step = "urgency"
        await reply("Når trenger du hjelp?\n\n1 = Akutt\n2 = I dag\n3 = Senere")

    elif step == "urgency":
        category = classify_urgency(inbound_text)

        if category == "akutt":
            conversation.urgency = "akutt"
            conversation.current_step = "done"
            alert = (
                f"🚨 AKUTT OPPDRAG\n\n"
                f"📞 {caller}\n"
                f"❗ {conversation.problem_description}\n"
                f"📍 {conversation.address}"
            )
            await provider.send_sms(to=customer.plumber_phone, from_=from_, body=alert)
            db.add(
                Message(
                    conversation_id=conversation.id,
                    direction="outbound",
                    body=f"[til rørlegger] {alert}",
                )
            )
            await reply("🚨 Dette er registrert som akutt. Rørlegger er varslet.")

        elif category in ("i dag", "senere"):
            conversation.urgency = category
            conversation.current_step = "done"
            await reply(
                f"Takk! Henvendelsen er mottatt.\n\n"
                f"Du kan selv velge tidspunkt her:\n{customer.calendly_url}"
            )

        else:
            await reply(
                "Jeg forsto ikke svaret.\n\nSvar med:\n1 = Akutt\n2 = I dag\n3 = Senere"
            )

    conversation.updated_at = datetime.utcnow()
    await db.commit()
