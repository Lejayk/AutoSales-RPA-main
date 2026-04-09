"""infrastructure/uploader.py – Cloudinary image upload adapter."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

import cloudinary
import cloudinary.uploader

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


def upload_dashboard(image_path: str | Path) -> str:
    """Upload dashboard image to Cloudinary and return public HTTPS URL.

    Args:
        image_path: Local path to the dashboard PNG.

    Returns:
        Public HTTPS URL of the uploaded image.

    Raises:
        EnvironmentError: If Cloudinary env vars are missing.
        FileNotFoundError: If image_path does not exist.
    """
    cloud_name = _get_required_env("CLOUDINARY_CLOUD_NAME")
    api_key = _get_required_env("CLOUDINARY_API_KEY")
    api_secret = _get_required_env("CLOUDINARY_API_SECRET")

    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Dashboard image not found: {path}")

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )

    result = cloudinary.uploader.upload(
        str(path),
        folder="autosales-rpa",
        public_id="dashboard_resumen",
        overwrite=True,
        resource_type="image",
    )

    url: str = result["secure_url"]
    logger.info("Dashboard uploaded to Cloudinary: %s", url)
    return url
