from __future__ import annotations

import logging
import os

from app.providers.base import IncomingSMS, SMSProvider

logger = logging.getLogger(__name__)


class FortysixElksProvider(SMSProvider):
    """46elks SMS gateway provider.

    Incoming webhook (POST form data — all lowercase, unlike Twilio):
        from     → caller's phone number
        to       → your 46elks number
        message  → SMS body
        id       → 46elks message ID (informational)

    Outgoing API:
        POST https://api.46elks.com/a1/sms  (HTTP Basic Auth)
        Form fields: from, to, message

    Required environment variables when implemented:
        FORTYSIX_ELKS_API_USERNAME
        FORTYSIX_ELKS_API_PASSWORD

    Full docs: https://46elks.com/docs
    """

    provider_name = "46elks"
    _API_URL = "https://api.46elks.com/a1/sms"

    async def send_sms(self, to: str, from_: str, body: str) -> bool:
        username = os.getenv("FORTYSIX_ELKS_API_USERNAME")
        password = os.getenv("FORTYSIX_ELKS_API_PASSWORD")
        if not username or not password:
            logger.error(
                "46elks credentials not configured "
                "(set FORTYSIX_ELKS_API_USERNAME and FORTYSIX_ELKS_API_PASSWORD)"
            )
            return False

        # Uncomment and implement once a 46elks account is available:
        #
        # import httpx
        # try:
        #     async with httpx.AsyncClient() as client:
        #         resp = await client.post(
        #             self._API_URL,
        #             auth=(username, password),
        #             data={"from": from_, "to": to, "message": body},
        #         )
        #         resp.raise_for_status()
        #         result = resp.json()
        #         logger.info("46elks SMS sent to=%s id=%s", to, result.get("id"))
        #         return True
        # except Exception:
        #     logger.exception("Failed to send 46elks SMS to=%s", to)
        #     return False

        raise NotImplementedError(
            "46elks send_sms is not yet implemented. "
            "Uncomment the httpx block in FortysixElksProvider.send_sms once your account is ready."
        )

    def parse_incoming(self, request_data: dict) -> IncomingSMS:
        """Parse 46elks webhook form fields (lowercase: from, to, message)."""
        return IncomingSMS(
            from_number=(request_data.get("from") or "").strip(),
            to_number=(request_data.get("to") or "").strip(),
            body=(request_data.get("message") or "").strip(),
            provider=self.provider_name,
        )
