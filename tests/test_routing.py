"""Tests for SMS routing logic and conversation flow."""
import os
from datetime import datetime, timedelta
from unittest.mock import call

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.conversation import CONVERSATION_TIMEOUT_HOURS, MIN_PROBLEM_LENGTH
from app.main import seed_from_env_if_empty
from app.models import Conversation, Customer
from app.reminders import (
    EXPIRE_AFTER_REMINDER_HOURS,
    REMINDER_AFTER_HOURS,
    expire_stale_conversations,
    send_pending_reminders,
)
from tests.conftest import make_customer, mock_twilio_sms


# ──── Helper ──────────────────────────────────────────────────────────────────

async def sms(
    client: AsyncClient,
    *,
    from_: str = "+4799999999",
    to: str,
    body: str,
):
    return await client.post(
        "/incoming-sms",
        data={"From": from_, "To": to, "Body": body},
    )


# ──── Routing: customer lookup by To number ──────────────────────────────────

async def test_known_number_routes_to_correct_customer(db_session, http_client):
    """SMS to a registered Twilio number should route to that customer."""
    customer = await make_customer(db_session, twilio_number="+4711111111")

    with mock_twilio_sms():
        resp = await sms(http_client, to=customer.twilio_number, body="Hei")

    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_unknown_number_returns_unknown_status(db_session, http_client):
    """SMS to an unregistered number should return unknown_number."""
    await make_customer(db_session, twilio_number="+4711111111")

    with mock_twilio_sms():
        resp = await sms(http_client, to="+4700000000", body="Hei")

    assert resp.status_code == 200
    assert resp.json()["status"] == "unknown_number"


async def test_inactive_customer_is_ignored(db_session, http_client):
    """SMS to an inactive customer's number should be treated as unknown."""
    customer = await make_customer(db_session, is_active=False)

    with mock_twilio_sms():
        resp = await sms(http_client, to=customer.twilio_number, body="Hei")

    assert resp.json()["status"] == "unknown_number"


async def test_two_customers_route_independently(db_session, http_client):
    """Messages to different Twilio numbers should create separate conversations."""
    customer_a = await make_customer(
        db_session, twilio_number="+4711111111", plumber_phone="+4791111111"
    )
    customer_b = await make_customer(
        db_session, twilio_number="+4722222222", plumber_phone="+4792222222"
    )

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer_a.twilio_number, body="Lekkasje")
        await sms(http_client, to=customer_b.twilio_number, body="Lekkasje")

    # Each greeting was sent from the respective customer's Twilio number
    from_numbers = {c.kwargs["from_"] for c in mock_sms.call_args_list}
    assert customer_a.twilio_number in from_numbers
    assert customer_b.twilio_number in from_numbers

    # Two separate conversations created
    result = await db_session.execute(select(Conversation))
    conversations = result.scalars().all()
    assert len(conversations) == 2
    assert conversations[0].customer_id != conversations[1].customer_id


async def test_missing_body_is_ignored(db_session, http_client):
    """Requests without a Body field should be silently ignored."""
    resp = await http_client.post(
        "/incoming-sms", data={"From": "+4799999999", "To": "+4711111111"}
    )
    assert resp.json()["status"] == "ignored"


# ──── Conversation flow ───────────────────────────────────────────────────────

async def test_first_sms_sends_greeting(db_session, http_client):
    """First message from a new caller should trigger the greeting."""
    customer = await make_customer(db_session)

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="Hei")

    mock_sms.assert_called_once()
    assert mock_sms.call_args.kwargs["to"] == "+4799999999"
    # Greeting contains either company name or "hjelpe"
    body = mock_sms.call_args.kwargs["body"]
    assert customer.company_name in body or "hjelpe" in body.lower()


async def test_first_sms_creates_conversation_with_step_problem(db_session, http_client):
    """A new conversation should start at step 'problem'."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")

    result = await db_session.execute(
        select(Conversation).where(Conversation.customer_id == customer.id)
    )
    conv = result.scalar_one()
    assert conv.current_step == "problem"
    assert conv.caller_phone == "+4799999999"


async def test_step_problem_asks_for_address(db_session, http_client):
    """Second message (problem description) should prompt for address."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")  # greeting

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="Vannlekkasje under vasken")

    mock_sms.assert_called_once()
    assert "adresse" in mock_sms.call_args.kwargs["body"].lower()


async def test_step_address_asks_for_urgency(db_session, http_client):
    """After address is given, the urgency menu should be sent."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")
        await sms(http_client, to=customer.twilio_number, body="Lekkasje")

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="Storgata 1, Oslo")

    mock_sms.assert_called_once()
    body = mock_sms.call_args.kwargs["body"]
    assert "akutt" in body.lower()
    assert "1" in body


async def test_urgency_akutt_notifies_plumber_and_caller(db_session, http_client):
    """Responding '1' should alert the plumber and confirm to the caller."""
    customer = await make_customer(db_session, plumber_phone="+4791111111")
    caller = "+4799999999"

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")
        await sms(http_client, to=customer.twilio_number, body="Lekkasje")
        await sms(http_client, to=customer.twilio_number, body="Storgata 1")

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="1")

    assert mock_sms.call_count == 2

    plumber_call = next(
        c for c in mock_sms.call_args_list if c.kwargs["to"] == customer.plumber_phone
    )
    assert "AKUTT" in plumber_call.kwargs["body"]
    assert caller in plumber_call.kwargs["body"]

    caller_call = next(
        c for c in mock_sms.call_args_list if c.kwargs["to"] == caller
    )
    assert "varslet" in caller_call.kwargs["body"].lower()


async def test_urgency_akutt_keyword(db_session, http_client):
    """Responding 'akutt' (text) should also trigger the emergency flow."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")
        await sms(http_client, to=customer.twilio_number, body="Lekkasje")
        await sms(http_client, to=customer.twilio_number, body="Storgata 1")

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="Akutt")  # capital A

    plumber_call = next(
        c for c in mock_sms.call_args_list if c.kwargs["to"] == customer.plumber_phone
    )
    assert "AKUTT" in plumber_call.kwargs["body"]


async def test_urgency_non_akutt_sends_calendly_link(db_session, http_client):
    """Responding '2' should send the Calendly link."""
    customer = await make_customer(db_session, calendly_url="https://calendly.com/test/demo")

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")
        await sms(http_client, to=customer.twilio_number, body="Lekkasje")
        await sms(http_client, to=customer.twilio_number, body="Storgata 1")

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="2")

    mock_sms.assert_called_once()
    assert customer.calendly_url in mock_sms.call_args.kwargs["body"]


async def test_urgency_invalid_response_reprompts(db_session, http_client):
    """An unrecognised urgency response should re-ask without advancing the step."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")
        await sms(http_client, to=customer.twilio_number, body="Lekkasje")
        await sms(http_client, to=customer.twilio_number, body="Storgata 1")

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="vet ikke")

    mock_sms.assert_called_once()
    assert "forsto ikke" in mock_sms.call_args.kwargs["body"].lower()

    # Step should still be "urgency"
    result = await db_session.execute(
        select(Conversation).where(Conversation.customer_id == customer.id)
    )
    conv = result.scalar_one()
    assert conv.current_step == "urgency"


async def test_completed_conversation_starts_fresh(db_session, http_client):
    """A new message after a completed conversation should start a new conversation."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        # Complete a full conversation
        await sms(http_client, to=customer.twilio_number, body="start")
        await sms(http_client, to=customer.twilio_number, body="Lekkasje")
        await sms(http_client, to=customer.twilio_number, body="Storgata 1")
        await sms(http_client, to=customer.twilio_number, body="2")  # done

    with mock_twilio_sms() as mock_sms:
        # New message — should trigger greeting again
        await sms(http_client, to=customer.twilio_number, body="Hei igjen")

    assert "hjelpe" in mock_sms.call_args.kwargs["body"].lower()

    result = await db_session.execute(
        select(Conversation).where(Conversation.customer_id == customer.id)
    )
    conversations = result.scalars().all()
    assert len(conversations) == 2


async def test_expired_conversation_starts_fresh(db_session, http_client):
    """A message after CONVERSATION_TIMEOUT_HOURS should start a new conversation."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")

    # Manually expire the conversation
    result = await db_session.execute(
        select(Conversation).where(Conversation.customer_id == customer.id)
    )
    conv = result.scalar_one()
    conv.updated_at = datetime.utcnow() - timedelta(
        hours=CONVERSATION_TIMEOUT_HOURS + 1
    )
    await db_session.commit()

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="Ny henvendelse")

    # Greeting should be sent again
    assert "hjelpe" in mock_sms.call_args.kwargs["body"].lower()

    result = await db_session.execute(
        select(Conversation).where(Conversation.customer_id == customer.id)
    )
    conversations = result.scalars().all()
    assert len(conversations) == 2


# ──── Custom greeting message ─────────────────────────────────────────────────

async def test_custom_greeting_message_is_used(db_session, http_client):
    """A customer with a custom greeting_message should use it instead of the default."""
    customer = await make_customer(db_session)
    customer.greeting_message = "Velkommen til Rørfiks! Hva kan vi hjelpe med?"
    await db_session.commit()

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="start")

    assert "Rørfiks" in mock_sms.call_args.kwargs["body"]


# ──── Personalisering ─────────────────────────────────────────────────────────

async def test_greeting_includes_company_name(db_session, http_client):
    """Default greeting should include the customer's company_name."""
    customer = await make_customer(db_session, company_name="Bergen VVS AS")

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="start")

    assert "Bergen VVS AS" in mock_sms.call_args.kwargs["body"]


async def test_custom_greeting_overrides_company_name(db_session, http_client):
    """Explicit greeting_message must take priority over company_name interpolation."""
    customer = await make_customer(db_session, company_name="Bergen VVS AS")
    customer.greeting_message = "Hei fra Rørfix!"
    await db_session.commit()

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="start")

    body = mock_sms.call_args.kwargs["body"]
    assert "Rørfix" in body
    assert "Bergen VVS AS" not in body


# ──── Kortbeskrivelse av problem ──────────────────────────────────────────────

async def test_short_problem_description_reprompts(db_session, http_client):
    """Problem description shorter than MIN_PROBLEM_LENGTH should trigger a reprompt."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")  # greeting

    short_body = "x" * (MIN_PROBLEM_LENGTH - 1)  # one char too short
    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body=short_body)

    mock_sms.assert_called_once()
    assert "detaljert" in mock_sms.call_args.kwargs["body"].lower()

    # Conversation must still be at "problem" step
    result = await db_session.execute(
        select(Conversation).where(Conversation.customer_id == customer.id)
    )
    assert result.scalar_one().current_step == "problem"


async def test_exact_min_length_problem_proceeds(db_session, http_client):
    """Problem description of exactly MIN_PROBLEM_LENGTH characters should be accepted."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")

    exact_body = "x" * MIN_PROBLEM_LENGTH
    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body=exact_body)

    assert "adresse" in mock_sms.call_args.kwargs["body"].lower()


# ──── Utvidet hastegrad-parsing ───────────────────────────────────────────────

async def _reach_urgency_step(http_client, twilio_number):
    """Helper: advance a conversation to the urgency step."""
    with mock_twilio_sms():
        await sms(http_client, to=twilio_number, body="start")
        await sms(http_client, to=twilio_number, body="Lekkasje under vasken")
        await sms(http_client, to=twilio_number, body="Storgata 1, Oslo")


async def test_urgency_haster_keyword(db_session, http_client):
    """'haster' as free text should trigger the emergency flow."""
    customer = await make_customer(db_session)
    await _reach_urgency_step(http_client, customer.twilio_number)

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="Det haster virkelig")

    plumber_calls = [c for c in mock_sms.call_args_list if c.kwargs["to"] == customer.plumber_phone]
    assert len(plumber_calls) == 1
    assert "AKUTT" in plumber_calls[0].kwargs["body"]


async def test_urgency_neste_uke_phrase(db_session, http_client):
    """'neste uke' should send Calendly link (ikke-akutt)."""
    customer = await make_customer(db_session)
    await _reach_urgency_step(http_client, customer.twilio_number)

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="Neste uke passer bra")

    mock_sms.assert_called_once()
    assert customer.calendly_url in mock_sms.call_args.kwargs["body"]


async def test_urgency_ikke_haster_is_later_not_akutt(db_session, http_client):
    """'ikke haster' must route to Calendly, NOT trigger the emergency flow."""
    customer = await make_customer(db_session)
    await _reach_urgency_step(http_client, customer.twilio_number)

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="Ikke haster")

    # No message to plumber
    plumber_calls = [c for c in mock_sms.call_args_list if c.kwargs["to"] == customer.plumber_phone]
    assert len(plumber_calls) == 0
    # Calendly link sent to caller
    assert customer.calendly_url in mock_sms.call_args.kwargs["body"]


async def test_urgency_idag_word(db_session, http_client):
    """'idag' (one word) should be accepted as a valid non-urgent response."""
    customer = await make_customer(db_session)
    await _reach_urgency_step(http_client, customer.twilio_number)

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="idag")

    assert customer.calendly_url in mock_sms.call_args.kwargs["body"]


async def test_urgency_stores_category_in_db(db_session, http_client):
    """Resolved urgency category should be persisted in conversation.urgency."""
    customer = await make_customer(db_session)
    await _reach_urgency_step(http_client, customer.twilio_number)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="neste uke")

    result = await db_session.execute(
        select(Conversation).where(Conversation.customer_id == customer.id)
    )
    conv = result.scalar_one()
    assert conv.urgency == "senere"
    assert conv.current_step == "done"


# ──── Påminnelser og utløp ────────────────────────────────────────────────────

async def test_reminder_sent_to_stale_conversation(db_session, http_client):
    """Conversations inactive for REMINDER_AFTER_HOURS should receive a reminder SMS."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")
        await sms(http_client, to=customer.twilio_number, body="Lekkasje")

    # Make conversation stale
    result = await db_session.execute(
        select(Conversation).where(Conversation.customer_id == customer.id)
    )
    conv = result.scalar_one()
    conv.updated_at = datetime.utcnow() - timedelta(hours=REMINDER_AFTER_HOURS + 1)
    await db_session.commit()

    with mock_twilio_sms() as mock_sms:
        count = await send_pending_reminders(db_session)

    assert count == 1
    mock_sms.assert_called_once()
    assert mock_sms.call_args.kwargs["to"] == conv.caller_phone
    assert "Trenger du" in mock_sms.call_args.kwargs["body"]


async def test_reminder_not_sent_twice(db_session, http_client):
    """A conversation that already has reminder_sent_at should not receive another reminder."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")

    result = await db_session.execute(
        select(Conversation).where(Conversation.customer_id == customer.id)
    )
    conv = result.scalar_one()
    conv.updated_at = datetime.utcnow() - timedelta(hours=REMINDER_AFTER_HOURS + 1)
    conv.reminder_sent_at = datetime.utcnow() - timedelta(hours=1)  # already reminded
    await db_session.commit()

    with mock_twilio_sms() as mock_sms:
        count = await send_pending_reminders(db_session)

    assert count == 0
    mock_sms.assert_not_called()


async def test_reminder_not_sent_to_recent_conversation(db_session, http_client):
    """A conversation with recent activity should not receive a reminder."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")

    # updated_at is still "just now" — not stale
    with mock_twilio_sms() as mock_sms:
        count = await send_pending_reminders(db_session)

    assert count == 0
    mock_sms.assert_not_called()


async def test_conversation_expires_after_no_response_to_reminder(db_session, http_client):
    """Conversation should be marked 'expired' when EXPIRE_AFTER_REMINDER_HOURS elapse."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")

    result = await db_session.execute(
        select(Conversation).where(Conversation.customer_id == customer.id)
    )
    conv = result.scalar_one()
    conv.reminder_sent_at = datetime.utcnow() - timedelta(
        hours=EXPIRE_AFTER_REMINDER_HOURS + 1
    )
    await db_session.commit()

    count = await expire_stale_conversations(db_session)

    assert count == 1
    await db_session.refresh(conv)
    assert conv.current_step == "expired"


async def test_done_conversation_not_expired(db_session, http_client):
    """Completed conversations ('done') must not be touched by the expiry job."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")
        await sms(http_client, to=customer.twilio_number, body="Lekkasje")
        await sms(http_client, to=customer.twilio_number, body="Storgata 1")
        await sms(http_client, to=customer.twilio_number, body="2")  # → done

    result = await db_session.execute(
        select(Conversation).where(Conversation.customer_id == customer.id)
    )
    conv = result.scalar_one()
    # Simulate old reminder_sent_at even though step is "done"
    conv.reminder_sent_at = datetime.utcnow() - timedelta(hours=EXPIRE_AFTER_REMINDER_HOURS + 1)
    await db_session.commit()

    count = await expire_stale_conversations(db_session)

    assert count == 0
    await db_session.refresh(conv)
    assert conv.current_step == "done"  # unchanged


async def test_expired_conversation_starts_new_on_next_sms(db_session, http_client):
    """After a conversation is expired, the next SMS should start a fresh conversation."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")

    # Manually expire
    result = await db_session.execute(
        select(Conversation).where(Conversation.customer_id == customer.id)
    )
    conv = result.scalar_one()
    conv.current_step = "expired"
    await db_session.commit()

    with mock_twilio_sms() as mock_sms:
        await sms(http_client, to=customer.twilio_number, body="Ny henvendelse")

    # Greeting sent for fresh conversation
    body = mock_sms.call_args.kwargs["body"]
    assert customer.company_name in body or "hjelpe" in body.lower()

    result = await db_session.execute(
        select(Conversation).where(Conversation.customer_id == customer.id)
    )
    assert len(result.scalars().all()) == 2


async def test_reminder_cleared_when_user_responds(db_session, http_client):
    """Responding after a reminder is sent should clear reminder_sent_at."""
    customer = await make_customer(db_session)

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="start")

    # Simulate that a reminder was already sent
    result = await db_session.execute(
        select(Conversation).where(Conversation.customer_id == customer.id)
    )
    conv = result.scalar_one()
    conv.reminder_sent_at = datetime.utcnow() - timedelta(hours=1)
    await db_session.commit()

    with mock_twilio_sms():
        await sms(http_client, to=customer.twilio_number, body="Lekkasje under vasken")

    await db_session.refresh(conv)
    assert conv.reminder_sent_at is None


# ──── Webhook endpoints ───────────────────────────────────────────────────────

async def test_webhook_twilio_endpoint(db_session, http_client):
    """/webhook/twilio should work identically to /incoming-sms."""
    customer = await make_customer(db_session)

    with mock_twilio_sms() as mock_sms:
        resp = await http_client.post(
            "/webhook/twilio",
            data={"From": "+4799999999", "To": customer.twilio_number, "Body": "Hei"},
        )

    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    mock_sms.assert_called_once()


async def test_webhook_46elks_endpoint(db_session, http_client):
    """/webhook/46elks parses lowercase 46elks form fields."""
    from unittest.mock import patch, AsyncMock
    from app.providers.fortysix_elks import FortysixElksProvider

    customer = await make_customer(db_session)

    with patch.object(
        FortysixElksProvider, "send_sms", new_callable=AsyncMock, return_value=True
    ) as mock_sms:
        resp = await http_client.post(
            "/webhook/46elks",
            data={"from": "+4799999999", "to": customer.twilio_number, "message": "Hei"},
        )

    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    mock_sms.assert_called_once()


# ──── Env var backward compatibility ─────────────────────────────────────────

async def test_seed_from_env_creates_default_customer(db_session):
    """seed_from_env_if_empty should create a customer if the table is empty."""
    with patch.dict(
        os.environ,
        {
            "TWILIO_NUMBER": "+4711111111",
            "PLUMBER_PHONE": "+4799999999",
            "CALENDLY_URL": "https://calendly.com/test",
        },
    ):
        await seed_from_env_if_empty(db_session)

    result = await db_session.execute(select(Customer))
    customers = result.scalars().all()
    assert len(customers) == 1
    assert customers[0].twilio_number == "+4711111111"
    assert customers[0].plumber_phone == "+4799999999"


async def test_seed_from_env_does_not_overwrite_existing(db_session):
    """seed_from_env_if_empty should not run if the table already has customers."""
    await make_customer(db_session, twilio_number="+4700000001")

    with patch.dict(os.environ, {"TWILIO_NUMBER": "+4700000002", "PLUMBER_PHONE": "+4799999999"}):
        await seed_from_env_if_empty(db_session)

    result = await db_session.execute(select(Customer))
    customers = result.scalars().all()
    assert len(customers) == 1  # Only the original one
    assert customers[0].twilio_number == "+4700000001"


async def test_seed_from_env_skips_if_no_env_vars(db_session):
    """seed_from_env_if_empty should do nothing if TWILIO_NUMBER is not set."""
    env = {k: v for k, v in os.environ.items() if k not in ("TWILIO_NUMBER", "PLUMBER_PHONE")}
    with patch.dict(os.environ, env, clear=True):
        await seed_from_env_if_empty(db_session)

    result = await db_session.execute(select(Customer))
    assert result.scalars().all() == []
