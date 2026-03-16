from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

from twilio.rest import Client

from app.providers.base import IncomingSMS, SMSProvider

logger = logging.getLogger(__name__)

_client: Optional[Client] = None


def _get_client() -> Client:
    global _client
    if _client is None:
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        if not sid or not token:
            raise RuntimeError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set")
        _client = Client(sid, token)
    return _client


class TwilioProvider(SMSProvider):
    provider_name = "twilio"

    async def send_sms(self, to: str, from_: str, body: str) -> bool:
        """Send via Twilio REST API (runs blocking SDK call in a thread pool)."""

        def _call() -> str:
            msg = _get_client().messages.create(to=to, from_=from_, body=body)
            return msg.sid

        try:
            sid = await asyncio.to_thread(_call)
            logger.info("Twilio SMS sent to=%s sid=%s", to, sid)
            return True
        except Exception:
            logger.exception("Failed to send Twilio SMS to=%s", to)
            return False

    def parse_incoming(self, request_data: dict) -> IncomingSMS:
        """Parse Twilio webhook form fields (PascalCase: From, To, Body)."""
        return IncomingSMS(
            from_number=(request_data.get("From") or "").strip(),
            to_number=(request_data.get("To") or "").strip(),
            body=(request_data.get("Body") or "").strip(),
            provider=self.provider_name,
        )
