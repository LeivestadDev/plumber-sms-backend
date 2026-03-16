from __future__ import annotations

import logging
import os

from twilio.rest import Client

logger = logging.getLogger(__name__)

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        if not sid or not token:
            raise RuntimeError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set")
        _client = Client(sid, token)
    return _client


def send_sms(to: str, from_: str, body: str) -> str:
    msg = _get_client().messages.create(to=to, from_=from_, body=body)
    logger.info("SMS sent to=%s sid=%s", to, msg.sid)
    return msg.sid
