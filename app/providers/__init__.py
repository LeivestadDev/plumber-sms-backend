from app.providers.base import SUPPORTED_PROVIDERS, IncomingSMS, SMSProvider
from app.providers.fortysix_elks import FortysixElksProvider
from app.providers.twilio_provider import TwilioProvider


def get_provider(name: str) -> SMSProvider:
    """Return a fresh SMSProvider instance for the given provider name."""
    if name == "twilio":
        return TwilioProvider()
    if name == "46elks":
        return FortysixElksProvider()
    raise ValueError(
        f"Unknown SMS provider: {name!r}. Valid options: {SUPPORTED_PROVIDERS}"
    )


__all__ = [
    "IncomingSMS",
    "SMSProvider",
    "TwilioProvider",
    "FortysixElksProvider",
    "get_provider",
    "SUPPORTED_PROVIDERS",
]
