"""main.py – AutoSales-RPA orchestration entry point.

Flow:
    Extract -> Analyze -> Graph -> Notify
"""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from twilio.base.exceptions import TwilioRestException

# ── Project root discovery ─────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parents[1]
DATA_FILE = ROOT_DIR / "data" / "Ventas Fundamentos.xlsx"
OUTPUT_DIR = ROOT_DIR / "output"
DASHBOARD_PATH = OUTPUT_DIR / "dashboard_resumen.png"
LOG_PATH = OUTPUT_DIR / "rpa_sales.log"

# ── Load .env before importing project modules that read env vars ──────────
load_dotenv(ROOT_DIR / ".env")

# Add src/ to the import path so modules can be imported directly
sys.path.insert(0, str(Path(__file__).parent))

from core.extraction import load_and_merge     # noqa: E402
from core.analytics import compute_all_kpis    # noqa: E402
from core.visualization import build_dashboard # noqa: E402
from infrastructure.notifier import send_whatsapp_report, build_summary_text  # noqa: E402


# ── Logging setup ──────────────────────────────────────────────────────────

def configure_logging(log_path: Path) -> None:
    """Configure root logger to write to both stdout and a log file.

    Args:
        log_path: Destination path for the log file.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        datefmt=datefmt,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
    )


# ── Orchestrator ───────────────────────────────────────────────────────────

def run() -> None:
    """Run full modular RPA workflow with robust error handling."""
    logger = logging.getLogger(__name__)
    logger.info("╔══════════════════════════════════════╗")
    logger.info("║   AutoSales-RPA  —  Starting run     ║")
    logger.info("╚══════════════════════════════════════╝")

    # ── Step 1: Extract ────────────────────────────────────────────────────
    try:
        merged_df = load_and_merge(DATA_FILE)
    except FileNotFoundError as exc:
        logger.error("Data file missing: %s", exc)
        sys.exit(1)
    except KeyError as exc:
        logger.error("Missing required data columns: %s", exc)
        sys.exit(1)
    except Exception as exc:
        logger.exception("Unexpected error during data extraction: %s", exc)
        sys.exit(1)

    # ── Step 2: Analyze ────────────────────────────────────────────────────
    try:
        kpis = compute_all_kpis(merged_df)
    except KeyError as exc:
        logger.error("KPI computation failed due to missing columns: %s", exc)
        sys.exit(1)
    except Exception as exc:
        logger.exception("Error computing KPIs: %s", exc)
        sys.exit(1)

    # ── Step 3: Graph ──────────────────────────────────────────────────────
    try:
        saved_path = build_dashboard(
            sales_by_sede=kpis["sales_by_sede"],
            top_models=kpis["top_models"],
            sales_by_segmento=kpis["sales_by_segmento"],
            sales_by_canal=kpis["sales_by_canal"],
            output_path=DASHBOARD_PATH,
            style="seaborn-v0_8",
        )
        logger.info("Dashboard saved: %s", saved_path)
    except Exception as exc:
        logger.exception("Error generating dashboard: %s", exc)
        sys.exit(1)

    # ── Step 4: Notify ─────────────────────────────────────────────────────
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    twilio_from = os.getenv("TWILIO_FROM", "").strip()
    twilio_to = os.getenv("TWILIO_TO", "").strip()
    if not all([twilio_sid, twilio_token, twilio_from, twilio_to]):
        logger.warning(
            "Twilio environment variables are incomplete — skipping WhatsApp notification."
        )
    else:
        try:
            summary = build_summary_text(
                total_billed=kpis["total_billed"],
                total_sales=kpis["total_sales"],
                unique_clients=kpis["unique_clients"],
                top_models_series=kpis["top_models"],
            )
            # NOTE: media_url must be a publicly accessible URL.
            # Set the DASHBOARD_URL environment variable to enable image attachment.
            media_url = os.getenv("DASHBOARD_URL") or None
            send_whatsapp_report(
                summary_text=summary,
                dashboard_path=saved_path,
                media_url=media_url,
            )
        except EnvironmentError as exc:
            logger.error("Twilio configuration error: %s", exc)
        except TwilioRestException as exc:
            logger.error("Twilio connection/API error: %s", exc)
        except Exception as exc:
            logger.exception("Failed to send WhatsApp notification: %s", exc)

    logger.info("AutoSales-RPA run complete.")


if __name__ == "__main__":
    configure_logging(LOG_PATH)
    run()
