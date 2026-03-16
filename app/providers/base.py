from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

SUPPORTED_PROVIDERS = ("twilio", "46elks")


@dataclass
class IncomingSMS:
    """Normalised representation of an incoming SMS webhook payload."""

    from_number: str
    to_number: str
    body: str
    provider: str  # "twilio" | "46elks"


class SMSProvider(ABC):
    """Abstract base class for SMS gateway providers.

    Subclasses must:
    - Set the class attribute ``provider_name``
    - Implement ``send_sms`` (async, returns True/False — never raises)
    - Implement ``parse_incoming`` (sync, maps raw webhook dict → IncomingSMS)
    """

    provider_name: str  # overridden by subclasses

    @abstractmethod
    async def send_sms(self, to: str, from_: str, body: str) -> bool:
        """Send an outgoing SMS.

        Returns True on success, False on failure.
        Must not raise — catch and log exceptions internally.
        """
        ...

    @abstractmethod
    def parse_incoming(self, request_data: dict) -> IncomingSMS:
        """Parse a provider-specific webhook payload into a normalised IncomingSMS."""
        ...
