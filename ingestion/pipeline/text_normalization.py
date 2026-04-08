"""Batch 2.1 deterministic text normalization helpers.

Implements:
- encoding detection and decode standardization
- German character normalization and transliteration policy
- deterministic cleaning for cross-system joins
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


GERMAN_TRANSLITERATION = {
    "ä": "ae",
    "ö": "oe",
    "ü": "ue",
    "Ä": "Ae",
    "Ö": "Oe",
    "Ü": "Ue",
    "ß": "ss",
}


@dataclass(frozen=True)
class NormalizedText:
    display_text: str
    join_key_text: str
    source_encoding: str


def detect_encoding(raw_bytes: bytes) -> str:
    """Detect supported encodings deterministically.

    Preference order matches expected source systems:
    utf-8 -> utf-8-sig -> cp1252 -> latin-1.
    """
    for candidate in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            raw_bytes.decode(candidate)
            return candidate
        except UnicodeDecodeError:
            continue
    return "latin-1"


def decode_text(raw: bytes | str) -> tuple[str, str]:
    if isinstance(raw, str):
        return raw, "unicode"

    encoding = detect_encoding(raw)
    return raw.decode(encoding), encoding


def _strip_control_chars(text: str) -> str:
    return "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in ("\n", "\t"))


def transliterate_german(text: str) -> str:
    return "".join(GERMAN_TRANSLITERATION.get(ch, ch) for ch in text)


def clean_display_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = _strip_control_chars(normalized)
    normalized = normalized.replace("\u00a0", " ")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def build_join_key(text: str) -> str:
    normalized = clean_display_text(text)
    normalized = transliterate_german(normalized)
    normalized = normalized.casefold()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized


def normalize_text(raw: bytes | str) -> NormalizedText:
    decoded_text, source_encoding = decode_text(raw)
    display_text = clean_display_text(decoded_text)
    join_key_text = build_join_key(decoded_text)
    return NormalizedText(display_text=display_text, join_key_text=join_key_text, source_encoding=source_encoding)
