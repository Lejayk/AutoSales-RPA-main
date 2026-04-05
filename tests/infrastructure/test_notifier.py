"""Tests for src/infrastructure/notifier.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.infrastructure.notifier import build_summary_text, send_whatsapp_report


class _FakeMessage:
    def __init__(self, sid: str) -> None:
        self.sid = sid


class _FakeMessagesApi:
    def create(self, **kwargs):  # noqa: ANN003, ANN201
        return _FakeMessage("SM_TEST_123")


class _FakeClient:
    def __init__(self, account_sid: str, auth_token: str) -> None:
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.messages = _FakeMessagesApi()


def test_build_summary_text_contains_expected_fields() -> None:
    import pandas as pd

    top_models = pd.Series({"Yaris": 10, "Rio": 9})
    summary = build_summary_text(
        total_billed=123456.78,
        total_sales=21,
        unique_clients=19,
        top_models_series=top_models,
    )

    assert "Total facturado" in summary
    assert "Total ventas" in summary
    assert "Clientes únicos" in summary


def test_send_whatsapp_report_raises_if_env_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TWILIO_ACCOUNT_SID", raising=False)
    monkeypatch.delenv("TWILIO_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("TWILIO_FROM", raising=False)
    monkeypatch.delenv("TWILIO_TO", raising=False)

    with pytest.raises(EnvironmentError):
        send_whatsapp_report("test", Path("dashboard.png"))


def test_send_whatsapp_report_success_with_mock_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "AC_TEST")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "TOKEN_TEST")
    monkeypatch.setenv("TWILIO_FROM", "whatsapp:+14155238886")
    monkeypatch.setenv("TWILIO_TO", "whatsapp:+51999999999")
    monkeypatch.setattr("src.infrastructure.notifier.Client", _FakeClient)

    sid = send_whatsapp_report(
        summary_text="Resumen",
        dashboard_path=Path("dashboard.png"),
        media_url="https://example.com/dashboard.png",
    )
    assert sid == "SM_TEST_123"
