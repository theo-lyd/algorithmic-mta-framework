"""Batch 2.2 financial and numeric normalization helpers.

Implements:
- abbreviation parsing (million/billion forms)
- locale-aware numeric standardization
- currency normalization to EUR with effective-date policy
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date


MAGNITUDE_MAP = {
    "k": 1_000,
    "thousand": 1_000,
    "tsd": 1_000,
    "m": 1_000_000,
    "mn": 1_000_000,
    "mio": 1_000_000,
    "million": 1_000_000,
    "b": 1_000_000_000,
    "bn": 1_000_000_000,
    "mrd": 1_000_000_000,
    "billion": 1_000_000_000,
}


CURRENCY_SYMBOLS = {
    "EUR": "EUR",
    "€": "EUR",
    "USD": "USD",
    "$": "USD",
    "GBP": "GBP",
    "£": "GBP",
    "CHF": "CHF",
}


# Effective-date policy table (illustrative deterministic rates for pipeline normalization tests).
FX_RATE_POLICY = {
    "USD": [
        (date(2026, 1, 1), 0.92),
        (date(2026, 4, 1), 0.90),
    ],
    "GBP": [
        (date(2026, 1, 1), 1.18),
        (date(2026, 4, 1), 1.16),
    ],
    "CHF": [
        (date(2026, 1, 1), 1.03),
        (date(2026, 4, 1), 1.02),
    ],
    "EUR": [
        (date(1900, 1, 1), 1.0),
    ],
}


@dataclass(frozen=True)
class CurrencyNormalized:
    original_text: str
    amount_native: float
    currency: str
    effective_date: str
    fx_rate_to_eur: float
    amount_eur: float


def standardize_numeric_token(token: str) -> float:
    """Normalize locale-specific decimal/thousands separators.

    Examples:
    - "1.234,56" -> 1234.56
    - "1,234.56" -> 1234.56
    - "1 234,56" -> 1234.56
    """
    cleaned = token.strip().replace(" ", "")

    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "")
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        parts = cleaned.split(",")
        if len(parts[-1]) in (1, 2):
            cleaned = cleaned.replace(".", "")
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    else:
        cleaned = cleaned.replace(",", "")

    return float(cleaned)


def parse_abbreviated_amount(raw_text: str) -> float:
    """Parse abbreviations like Mio/Mrd/million/billion forms."""
    value = raw_text.strip().lower()
    value = value.replace("eur", "").replace(
        "usd", "").replace("gbp", "").replace("chf", "")
    value = value.replace("€", "").replace("$", "").replace("£", "")
    value = re.sub(r"\s+", " ", value).strip()

    match = re.match(r"^([-+]?[^a-z]+)\s*([a-z]+)?$", value)
    if not match:
        raise ValueError(f"Cannot parse amount: {raw_text}")

    number_token = match.group(1).strip()
    suffix = (match.group(2) or "").strip()

    number = standardize_numeric_token(number_token)
    multiplier = MAGNITUDE_MAP.get(suffix, 1)
    return number * multiplier


def detect_currency(raw_text: str, currency_hint: str | None = None) -> str:
    if currency_hint:
        hinted = currency_hint.upper()
        if hinted in CURRENCY_SYMBOLS:
            return CURRENCY_SYMBOLS[hinted]
        return hinted

    for symbol, code in CURRENCY_SYMBOLS.items():
        if symbol in raw_text:
            return code
    return "EUR"


def fx_rate_to_eur(currency: str, effective_dt: date) -> float:
    schedule = FX_RATE_POLICY.get(currency)
    if not schedule:
        raise ValueError(f"Unsupported currency: {currency}")

    selected_rate = None
    for start_dt, rate in sorted(schedule, key=lambda x: x[0]):
        if effective_dt >= start_dt:
            selected_rate = rate
        else:
            break

    if selected_rate is None:
        raise ValueError(
            f"No FX rate configured for {currency} at {effective_dt.isoformat()}")
    return selected_rate


def normalize_currency_to_eur(raw_text: str, effective_dt: date, currency_hint: str | None = None) -> CurrencyNormalized:
    currency = detect_currency(raw_text, currency_hint=currency_hint)
    amount_native = parse_abbreviated_amount(raw_text)
    rate = fx_rate_to_eur(currency, effective_dt)
    amount_eur = round(amount_native * rate, 2)

    return CurrencyNormalized(
        original_text=raw_text,
        amount_native=amount_native,
        currency=currency,
        effective_date=effective_dt.isoformat(),
        fx_rate_to_eur=rate,
        amount_eur=amount_eur,
    )
