from __future__ import annotations

import json
import unittest
from pathlib import Path

from ingestion.pipeline.text_normalization import (
    build_join_key,
    clean_display_text,
    decode_text,
    detect_encoding,
    normalize_text,
)


class TestTextNormalization(unittest.TestCase):
    def test_detect_encoding_utf8(self) -> None:
        raw = "München".encode("utf-8")
        self.assertEqual(detect_encoding(raw), "utf-8")

    def test_detect_encoding_cp1252(self) -> None:
        raw = "Köln €".encode("cp1252")
        self.assertEqual(detect_encoding(raw), "cp1252")

    def test_decode_bytes_roundtrip(self) -> None:
        raw = "Straße".encode("utf-8")
        decoded, encoding = decode_text(raw)
        self.assertEqual(decoded, "Straße")
        self.assertEqual(encoding, "utf-8")

    def test_deterministic_cleaning_from_fixtures(self) -> None:
        fixture_path = Path(
            "tests/fixtures/phase2/text_cleaning_fixtures.json")
        fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))

        for case in fixtures:
            normalized = normalize_text(case["raw_text"])
            self.assertEqual(normalized.display_text,
                             case["expected_display_text"])
            self.assertEqual(normalized.join_key_text,
                             case["expected_join_key_text"])

    def test_join_key_policy(self) -> None:
        value = "München / Straße #1"
        self.assertEqual(build_join_key(value), "muenchen_strasse_1")

    def test_display_text_policy(self) -> None:
        value = "  Köln\u00a0\t\n Nord  "
        self.assertEqual(clean_display_text(value), "Köln Nord")


if __name__ == "__main__":
    unittest.main()
