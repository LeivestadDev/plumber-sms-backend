"""Unit tests for Norwegian urgency keyword classification."""
import pytest

from app.urgency import classify_urgency


@pytest.mark.parametrize(
    "text,expected",
    [
        # ── Digits ────────────────────────────────────────────────────────────
        ("1", "akutt"),
        ("2", "i dag"),
        ("3", "senere"),
        # Digits embedded in text should NOT match as digit
        ("Leilighet 1", None),
        ("2 timer siden", None),
        # ── Akutt — enkeltord ─────────────────────────────────────────────────
        ("akutt", "akutt"),
        ("Akutt", "akutt"),
        ("AKUTT", "akutt"),
        ("Det haster!", "akutt"),
        ("Haster veldig", "akutt"),
        ("Dette er kritisk", "akutt"),
        ("Det er en nødsituasjon", "akutt"),
        ("Det er oversvømmelse i kjelleren", "akutt"),
        ("Vannet oversvømmer gulvet nå", "akutt"),
        ("ASAP", "akutt"),
        ("Ja asap takk", "akutt"),
        ("Rørbrudd i veggen", "akutt"),
        # ── Akutt — fraser ────────────────────────────────────────────────────
        ("Det lekker nå fra taket", "akutt"),
        ("Lekker akkurat nå", "akutt"),
        ("Vannet renner under vasken", "akutt"),
        ("Det renner nå", "akutt"),
        # ── I dag — enkeltord ─────────────────────────────────────────────────
        ("i dag", "i dag"),
        ("idag", "i dag"),
        ("Idag gjerne", "i dag"),
        ("Snarest", "i dag"),
        ("Snarest mulig", "i dag"),
        ("Gjerne i ettermiddag", "i dag"),
        ("I formiddag passer bra", "i dag"),
        # ── I dag — fraser ────────────────────────────────────────────────────
        ("i kveld passer", "i dag"),
        ("Kan dere komme i ettermiddag?", "i dag"),
        ("Så fort som mulig", "i dag"),
        ("Kan komme i morgen tidlig", "i dag"),
        # ── Senere — enkeltord ────────────────────────────────────────────────
        ("Befaring", "senere"),
        ("Jeg planlegger å renovere", "senere"),
        # ── Senere — fraser ───────────────────────────────────────────────────
        ("neste uke passer bra", "senere"),
        ("Neste uke", "senere"),
        ("Ikke haster", "senere"),
        ("Det ikke haster", "senere"),          # negation — must NOT match "haster" → akutt
        ("Ingen hast fra min side", "senere"),
        ("Ingen hastverk", "senere"),
        ("Når dere har tid", "senere"),
        ("Neste måned er greit", "senere"),
        ("Tar det med ro", "senere"),
        ("Om en stund", "senere"),
        # ── Ingen match ───────────────────────────────────────────────────────
        ("ja", None),
        ("nei", None),
        ("vet ikke", None),
        ("kanskje", None),
        ("ok", None),
        ("takk", None),
        ("hei", None),
        ("", None),
        ("   ", None),
    ],
)
def test_classify_urgency(text: str, expected):
    assert classify_urgency(text) == expected


def test_negation_case_ikke_haster():
    """Phrase 'ikke haster' must return 'senere' before the word 'haster' matches 'akutt'.

    Note: reversed word order ('haster ikke') is a known limitation of keyword matching
    without NLP — 'haster' is still matched as an urgent keyword in that case.
    """
    assert classify_urgency("ikke haster") == "senere"
    assert classify_urgency("Det ikke haster") == "senere"   # phrase present → later
    assert classify_urgency("Det haster ikke") == "akutt"   # reversed — word "haster" wins


def test_case_insensitivity():
    """Classification must be case-insensitive."""
    assert classify_urgency("AKUTT") == "akutt"
    assert classify_urgency("Haster") == "akutt"
    assert classify_urgency("I DAG") == "i dag"
    assert classify_urgency("NESTE UKE") == "senere"


def test_leading_trailing_whitespace():
    assert classify_urgency("  akutt  ") == "akutt"
    assert classify_urgency("  2  ") == "i dag"
