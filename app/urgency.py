"""Keyword-based urgency classification for Norwegian SMS responses.

Uses a two-pass approach: multi-word phrases are matched first (so "ikke haster"
correctly returns "senere" before the single word "haster" can match "akutt").
"""
import re
from typing import Optional

# ── Keyword lists ─────────────────────────────────────────────────────────────
# Single-word entries are matched against word tokens (exact word boundary).
# Multi-word entries are matched as substrings of the normalised text.

URGENT_KEYWORDS = [
    # single words
    "akutt", "haster", "nødsituasjon", "oversvømmelse", "oversvømmer",
    "oversvømt", "flom", "asap", "øyeblikkelig", "umiddelbart",
    "kritisk", "nødhjelp", "rørbrudd",
    # phrases
    "lekker nå", "renner nå", "vannet renner", "lekker akkurat nå",
]

TODAY_KEYWORDS = [
    # single words
    "idag", "snarest", "ettermiddag", "formiddag",
    # phrases
    "i dag", "i kveld", "i ettermiddag", "i formiddag",
    "så fort som mulig", "snarest mulig", "i morgen tidlig",
]

LATER_KEYWORDS = [
    # single words
    "befaring", "planlegger",
    # phrases (checked before single words — keeps "ikke haster" from matching URGENT)
    "neste uke", "ikke haster", "ingen hast", "ingen hastverk",
    "når dere har tid", "neste måned", "tar det med ro", "om en stund",
]

# Ordered list used by classify_urgency (priority: akutt > i dag > senere)
_CATEGORIES = [
    ("akutt", URGENT_KEYWORDS),
    ("i dag", TODAY_KEYWORDS),
    ("senere", LATER_KEYWORDS),
]

# Digits map — matched as exact full-message responses only
_DIGIT_MAP = {"1": "akutt", "2": "i dag", "3": "senere"}


def classify_urgency(text: str) -> Optional[str]:
    """Return 'akutt', 'i dag', 'senere', or None if no keyword matches.

    Matching order:
    1. Exact digit response ("1", "2", "3")
    2. Multi-word phrase match (all categories, akutt first)
    3. Single-word match (all categories, akutt first)
    """
    normalized = text.strip().lower()
    if not normalized:
        return None

    # 1. Exact digit
    if normalized in _DIGIT_MAP:
        return _DIGIT_MAP[normalized]

    # Split on non-word characters so "haster!" tokenises as "haster"
    words = set(re.split(r"\W+", normalized))

    # 2. Phrase matching (all categories before any single-word matching)
    for category, keywords in _CATEGORIES:
        for kw in keywords:
            if " " in kw and kw in normalized:
                return category

    # 3. Single-word matching
    for category, keywords in _CATEGORIES:
        for kw in keywords:
            if " " not in kw and kw in words:
                return category

    return None
