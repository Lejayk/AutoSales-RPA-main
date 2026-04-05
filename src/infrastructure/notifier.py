"""infrastructure/notifier.py – Twilio WhatsApp adapter."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)

load_dotenv()


def _get_required_env(var_name: str) -> str:
    """Return required environment variable value.

    Raises:
        EnvironmentError: If variable is missing or blank.
    """
    value = os.getenv(var_name, "").strip()
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{var_name}' is missing."
        )
    return value


def build_summary_text(
    total_billed: float,
    total_sales: int,
    unique_clients: int,
    top_models_series: pd.Series,
) -> str:
    """Build executive summary text for WhatsApp report."""
    top_lines = "\n".join(
        f"  {idx+1}. {model} ({units} ventas)"
        for idx, (model, units) in enumerate(top_models_series.items())
    )
    return (
        "📊 *AutoSales-RPA — Resumen Ejecutivo*\n\n"
        f"💵 Total facturado: S/. {total_billed:,.2f}\n"
        f"🧾 Total ventas: {total_sales}\n"
        f"👥 Clientes únicos: {unique_clients}\n\n"
        f"🏆 Top 5 modelos:\n{top_lines}\n\n"
        "_Reporte generado automáticamente._"
    )


def send_whatsapp_report(
    summary_text: str,
    dashboard_path: str | Path,
    media_url: str | None = None,
) -> str:
    """Send WhatsApp report via Twilio.

    Args:
        summary_text: Body text with KPI summary.
        dashboard_path: Local dashboard path (for traceability/logging).
        media_url: Public URL of the dashboard image (optional).

    Returns:
        Twilio message SID.

    Raises:
        EnvironmentError: If required env vars are missing.
        TwilioRestException: If Twilio API request fails.
    """
    account_sid = _get_required_env("TWILIO_ACCOUNT_SID")
    auth_token = _get_required_env("TWILIO_AUTH_TOKEN")
    from_number = _get_required_env("TWILIO_FROM")
    to_number = _get_required_env("TWILIO_TO")

    dashboard = Path(dashboard_path)
    logger.info("Sending WhatsApp report to %s with dashboard %s", to_number, dashboard.name)

    client = Client(account_sid, auth_token)

    payload: dict = {
        "from_": from_number,
        "to": to_number,
        "body": summary_text,
    }
    if media_url:
        payload["media_url"] = [media_url]

    try:
        message = client.messages.create(**payload)
        logger.info("WhatsApp report sent. SID=%s", message.sid)
        return message.sid
    except TwilioRestException:
        logger.exception("Twilio API call failed while sending report.")
        raise
