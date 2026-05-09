"""Tests de QR puros (sin DB)."""
from __future__ import annotations

import pytest

from app.modules.equipment.qr import build_payload, parse_payload


def test_qr_roundtrip() -> None:
    payload = build_payload("EQ-0001", "abcdef")
    code, token = parse_payload(payload)
    assert code == "EQ-0001"
    assert token == "abcdef"


def test_qr_invalid_json() -> None:
    with pytest.raises(ValueError):
        parse_payload("not-json")


def test_qr_wrong_version() -> None:
    with pytest.raises(ValueError):
        parse_payload('{"v":99,"code":"x","token":"y"}')
