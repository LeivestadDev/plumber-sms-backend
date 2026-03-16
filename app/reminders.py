"""Background job: send reminder SMS to stale conversations and expire non-responsive ones."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Conversation, Message
from app.providers import get_provider

logger = logging.getLogger(__name__)

# Send a reminder this many hours after the last message in an active conversation.
REMINDER_AFTER_HOURS = 2

# Expire (mark as "expired") this many hours after the reminder was sent with no response.
EXPIRE_AFTER_REMINDER_HOURS = 4

# How often the background worker polls (seconds).
CHECK_INTERVAL_SECONDS = 300  # 5 minutes

_TERMINAL_STEPS = ["done", "expired"]

REMINDER_BODY = (
    "Hei! Vi så du tok kontakt tidligere. "
    "Trenger du fortsatt hjelp? Svar for å fortsette."
)


async def send_pending_reminders(db: AsyncSession) -> int:
    """Send reminder SMS to conversations that have been inactive for REMINDER_AFTER_HOURS.

    Returns the number of reminders sent.
    """
    cutoff = datetime.utcnow() - timedelta(hours=REMINDER_AFTER_HOURS)

    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.customer))
        .where(
            ~Conversation.current_step.in_(_TERMINAL_STEPS),
            Conversation.updated_at <= cutoff,
            Conversation.reminder_sent_at.is_(None),
        )
    )
    conversations = result.scalars().all()

    count = 0
    for conv in conversations:
        customer = conv.customer
        provider = get_provider(customer.sms_provider)
        try:
            await provider.send_sms(to=conv.caller_phone, from_=customer.twilio_number, body=REMINDER_BODY)
            db.add(Message(conversation_id=conv.id, direction="outbound", body=REMINDER_BODY))
            conv.reminder_sent_at = datetime.utcnow()
            count += 1
        except Exception:
            logger.exception(
                "Failed to send reminder for conversation id=%d caller=%s",
                conv.id,
                conv.caller_phone,
            )

    if count:
        await db.commit()
        logger.info("Sent %d conversation reminder(s)", count)

    return count


async def expire_stale_conversations(db: AsyncSession) -> int:
    """Mark conversations as 'expired' when EXPIRE_AFTER_REMINDER_HOURS have passed
    since the reminder was sent with no further activity.

    Returns the number of conversations expired.
    """
    cutoff = datetime.utcnow() - timedelta(hours=EXPIRE_AFTER_REMINDER_HOURS)

    result = await db.execute(
        select(Conversation).where(
            ~Conversation.current_step.in_(_TERMINAL_STEPS),
            Conversation.reminder_sent_at.is_not(None),
            Conversation.reminder_sent_at <= cutoff,
        )
    )
    conversations = result.scalars().all()

    for conv in conversations:
        conv.current_step = "expired"
        conv.updated_at = datetime.utcnow()

    if conversations:
        await db.commit()
        logger.info("Expired %d stale conversation(s)", len(conversations))

    return len(conversations)


async def reminder_worker() -> None:
    """Long-running background task: expire stale conversations, then send reminders."""
    logger.info("Reminder worker started (interval=%ds)", CHECK_INTERVAL_SECONDS)
    while True:
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
        try:
            # Import here to avoid circular import at module load time
            from app.database import AsyncSessionLocal

            async with AsyncSessionLocal() as db:
                await expire_stale_conversations(db)
                await send_pending_reminders(db)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Unhandled error in reminder_worker")
