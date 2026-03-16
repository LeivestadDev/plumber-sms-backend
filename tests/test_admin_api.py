"""Tests for the admin REST API (/api/customers and /api/conversations)."""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from sqlalchemy import select

from app.models import Conversation, Message
from tests.conftest import make_customer

API_KEY = "test-secret-key"
HEADERS = {"X-API-Key": API_KEY}


@pytest.fixture(autouse=True)
def set_admin_api_key():
    with patch.dict(os.environ, {"ADMIN_API_KEY": API_KEY}):
        yield


# ── Helpers ───────────────────────────────────────────────────────────────────

def customer_payload(**overrides):
    return {
        "company_name": "Test Rørlegger AS",
        "twilio_number": "+4712345678",
        "plumber_phone": "+4798765432",
        "calendly_url": "https://calendly.com/test",
        **overrides,
    }


async def create_conversation_in_db(
    db,
    customer_id: int,
    *,
    step: str = "done",
    urgency: str | None = None,
    days_ago: int = 0,
) -> Conversation:
    ts = datetime.utcnow() - timedelta(days=days_ago)
    conv = Conversation(
        customer_id=customer_id,
        caller_phone="+4799999999",
        current_step=step,
        urgency=urgency,
        created_at=ts,
        updated_at=ts,
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


# ── Auth ──────────────────────────────────────────────────────────────────────

async def test_missing_api_key_returns_403(http_client):
    resp = await http_client.get("/api/customers")
    assert resp.status_code == 403


async def test_wrong_api_key_returns_403(http_client):
    resp = await http_client.get("/api/customers", headers={"X-API-Key": "wrong"})
    assert resp.status_code == 403


async def test_valid_api_key_grants_access(db_session, http_client):
    resp = await http_client.get("/api/customers", headers=HEADERS)
    assert resp.status_code == 200


async def test_unconfigured_api_key_returns_503(http_client):
    with patch.dict(os.environ, {}, clear=True):
        # Remove ADMIN_API_KEY from env entirely
        os.environ.pop("ADMIN_API_KEY", None)
        resp = await http_client.get("/api/customers", headers={"X-API-Key": "any"})
    assert resp.status_code == 503


# ── POST /api/customers ───────────────────────────────────────────────────────

async def test_create_customer_success(db_session, http_client):
    resp = await http_client.post(
        "/api/customers", json=customer_payload(), headers=HEADERS
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] > 0
    assert data["company_name"] == "Test Rørlegger AS"
    assert data["twilio_number"] == "+4712345678"
    assert data["is_active"] is True
    assert "created_at" in data


async def test_create_customer_with_greeting(db_session, http_client):
    resp = await http_client.post(
        "/api/customers",
        json=customer_payload(greeting_message="Hei fra Rørfix!"),
        headers=HEADERS,
    )
    assert resp.status_code == 201
    assert resp.json()["greeting_message"] == "Hei fra Rørfix!"


async def test_create_customer_duplicate_twilio_number_returns_409(db_session, http_client):
    await http_client.post("/api/customers", json=customer_payload(), headers=HEADERS)
    resp = await http_client.post(
        "/api/customers", json=customer_payload(), headers=HEADERS
    )
    assert resp.status_code == 409
    assert "twilio_number" in resp.json()["detail"]


async def test_create_customer_missing_required_field_returns_422(http_client):
    resp = await http_client.post(
        "/api/customers",
        json={"company_name": "Only name"},  # missing other fields
        headers=HEADERS,
    )
    assert resp.status_code == 422


# ── GET /api/customers ────────────────────────────────────────────────────────

async def test_list_customers_empty(db_session, http_client):
    resp = await http_client.get("/api/customers", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_customers_returns_all(db_session, http_client):
    await make_customer(db_session, twilio_number="+4711111111")
    await make_customer(db_session, twilio_number="+4722222222")
    resp = await http_client.get("/api/customers", headers=HEADERS)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_list_customers_filter_active_true(db_session, http_client):
    await make_customer(db_session, twilio_number="+4711111111", is_active=True)
    await make_customer(db_session, twilio_number="+4722222222", is_active=False)
    resp = await http_client.get("/api/customers?active=true", headers=HEADERS)
    data = resp.json()
    assert len(data) == 1
    assert data[0]["twilio_number"] == "+4711111111"


async def test_list_customers_filter_active_false(db_session, http_client):
    await make_customer(db_session, twilio_number="+4711111111", is_active=True)
    await make_customer(db_session, twilio_number="+4722222222", is_active=False)
    resp = await http_client.get("/api/customers?active=false", headers=HEADERS)
    data = resp.json()
    assert len(data) == 1
    assert data[0]["twilio_number"] == "+4722222222"


# ── GET /api/customers/{id} ───────────────────────────────────────────────────

async def test_get_customer_not_found_returns_404(http_client):
    resp = await http_client.get("/api/customers/9999", headers=HEADERS)
    assert resp.status_code == 404


async def test_get_customer_returns_stats(db_session, http_client):
    customer = await make_customer(db_session)
    now = datetime.utcnow()

    # 3 total: 2 recent (within 7 days), 1 old; 1 urgent
    await create_conversation_in_db(db_session, customer.id, urgency="akutt", days_ago=0)
    await create_conversation_in_db(db_session, customer.id, urgency="i dag", days_ago=3)
    await create_conversation_in_db(db_session, customer.id, days_ago=10)

    resp = await http_client.get(f"/api/customers/{customer.id}", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == customer.id
    assert data["stats"]["total_conversations"] == 3
    assert data["stats"]["conversations_last_7_days"] == 2
    assert data["stats"]["urgent_alerts_sent"] == 1


async def test_get_customer_zero_stats_when_no_conversations(db_session, http_client):
    customer = await make_customer(db_session)
    resp = await http_client.get(f"/api/customers/{customer.id}", headers=HEADERS)
    stats = resp.json()["stats"]
    assert stats == {"total_conversations": 0, "conversations_last_7_days": 0, "urgent_alerts_sent": 0}


# ── PATCH /api/customers/{id} ─────────────────────────────────────────────────

async def test_patch_customer_company_name(db_session, http_client):
    customer = await make_customer(db_session)
    resp = await http_client.patch(
        f"/api/customers/{customer.id}",
        json={"company_name": "Bergen VVS AS"},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["company_name"] == "Bergen VVS AS"
    assert resp.json()["twilio_number"] == customer.twilio_number  # unchanged


async def test_patch_customer_deactivate(db_session, http_client):
    customer = await make_customer(db_session, is_active=True)
    resp = await http_client.patch(
        f"/api/customers/{customer.id}",
        json={"is_active": False},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


async def test_patch_customer_clear_greeting(db_session, http_client):
    customer = await make_customer(db_session)
    customer.greeting_message = "Hei!"
    await db_session.commit()

    resp = await http_client.patch(
        f"/api/customers/{customer.id}",
        json={"greeting_message": None},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["greeting_message"] is None


async def test_patch_empty_body_is_noop(db_session, http_client):
    customer = await make_customer(db_session, company_name="Original Name")
    resp = await http_client.patch(
        f"/api/customers/{customer.id}", json={}, headers=HEADERS
    )
    assert resp.status_code == 200
    assert resp.json()["company_name"] == "Original Name"


async def test_patch_customer_not_found_returns_404(http_client):
    resp = await http_client.patch(
        "/api/customers/9999", json={"company_name": "X"}, headers=HEADERS
    )
    assert resp.status_code == 404


async def test_patch_customer_duplicate_twilio_number_returns_409(db_session, http_client):
    c1 = await make_customer(db_session, twilio_number="+4711111111")
    c2 = await make_customer(db_session, twilio_number="+4722222222")
    resp = await http_client.patch(
        f"/api/customers/{c2.id}",
        json={"twilio_number": c1.twilio_number},
        headers=HEADERS,
    )
    assert resp.status_code == 409


# ── GET /api/customers/{id}/conversations ─────────────────────────────────────

async def test_list_conversations_returns_all(db_session, http_client):
    customer = await make_customer(db_session)
    await create_conversation_in_db(db_session, customer.id, step="done")
    await create_conversation_in_db(db_session, customer.id, step="expired")
    await create_conversation_in_db(db_session, customer.id, step="problem")

    resp = await http_client.get(
        f"/api/customers/{customer.id}/conversations", headers=HEADERS
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 3


async def test_list_conversations_filter_active(db_session, http_client):
    customer = await make_customer(db_session)
    await create_conversation_in_db(db_session, customer.id, step="done")
    await create_conversation_in_db(db_session, customer.id, step="problem")

    resp = await http_client.get(
        f"/api/customers/{customer.id}/conversations?status=active", headers=HEADERS
    )
    data = resp.json()
    assert len(data) == 1
    assert data[0]["current_step"] == "problem"


async def test_list_conversations_filter_done(db_session, http_client):
    customer = await make_customer(db_session)
    await create_conversation_in_db(db_session, customer.id, step="done")
    await create_conversation_in_db(db_session, customer.id, step="expired")

    resp = await http_client.get(
        f"/api/customers/{customer.id}/conversations?status=done", headers=HEADERS
    )
    data = resp.json()
    assert len(data) == 1
    assert data[0]["current_step"] == "done"


async def test_list_conversations_filter_expired(db_session, http_client):
    customer = await make_customer(db_session)
    await create_conversation_in_db(db_session, customer.id, step="done")
    await create_conversation_in_db(db_session, customer.id, step="expired")

    resp = await http_client.get(
        f"/api/customers/{customer.id}/conversations?status=expired", headers=HEADERS
    )
    data = resp.json()
    assert len(data) == 1
    assert data[0]["current_step"] == "expired"


async def test_list_conversations_invalid_status_returns_422(db_session, http_client):
    customer = await make_customer(db_session)
    resp = await http_client.get(
        f"/api/customers/{customer.id}/conversations?status=invalid", headers=HEADERS
    )
    assert resp.status_code == 422


async def test_list_conversations_customer_not_found_returns_404(http_client):
    resp = await http_client.get("/api/customers/9999/conversations", headers=HEADERS)
    assert resp.status_code == 404


async def test_conversation_includes_expected_fields(db_session, http_client):
    customer = await make_customer(db_session)
    conv = await create_conversation_in_db(
        db_session, customer.id, step="done", urgency="akutt"
    )
    conv.problem_description = "Lekkasje"
    conv.address = "Storgata 1"
    await db_session.commit()

    resp = await http_client.get(
        f"/api/customers/{customer.id}/conversations", headers=HEADERS
    )
    item = resp.json()[0]
    assert item["id"] == conv.id
    assert item["problem_description"] == "Lekkasje"
    assert item["address"] == "Storgata 1"
    assert item["urgency"] == "akutt"
    assert item["current_step"] == "done"


# ── GET /api/conversations/{id}/messages ──────────────────────────────────────

async def test_list_messages_returns_ordered_messages(db_session, http_client):
    customer = await make_customer(db_session)
    conv = await create_conversation_in_db(db_session, customer.id)

    now = datetime.utcnow()
    msg1 = Message(
        conversation_id=conv.id, direction="inbound", body="Hei",
        created_at=now - timedelta(minutes=5),
    )
    msg2 = Message(
        conversation_id=conv.id, direction="outbound", body="Hei! Hva kan vi hjelpe med?",
        created_at=now - timedelta(minutes=4),
    )
    db_session.add_all([msg1, msg2])
    await db_session.commit()

    resp = await http_client.get(f"/api/conversations/{conv.id}/messages", headers=HEADERS)
    assert resp.status_code == 200
    messages = resp.json()
    assert len(messages) == 2
    assert messages[0]["direction"] == "inbound"
    assert messages[0]["body"] == "Hei"
    assert messages[1]["direction"] == "outbound"


async def test_list_messages_conversation_not_found_returns_404(http_client):
    resp = await http_client.get("/api/conversations/9999/messages", headers=HEADERS)
    assert resp.status_code == 404


async def test_list_messages_empty_conversation(db_session, http_client):
    customer = await make_customer(db_session)
    conv = await create_conversation_in_db(db_session, customer.id)
    resp = await http_client.get(f"/api/conversations/{conv.id}/messages", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == []


# ── SMS webhook is not protected ──────────────────────────────────────────────

async def test_incoming_sms_does_not_require_api_key(http_client):
    """The Twilio webhook endpoint must remain publicly accessible."""
    resp = await http_client.post(
        "/incoming-sms",
        data={"From": "+4799999999", "To": "+4711111111", "Body": "test"},
    )
    # Returns unknown_number (no customer) but NOT 403
    assert resp.status_code == 200
    assert resp.json()["status"] != 403
