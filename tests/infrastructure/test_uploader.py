"""Tests for src/infrastructure/uploader.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.infrastructure.uploader import upload_dashboard


class _FakeUploadResult(dict):
    """Simulates cloudinary.uploader.upload return value."""


class _FakeUploader:
    """Fake cloudinary.uploader module."""

    last_call_kwargs: dict | None = None

    @staticmethod
    def upload(file: str, **kwargs) -> dict:  # noqa: ANN003
        _FakeUploader.last_call_kwargs = {"file": file, **kwargs}
        return {"secure_url": "https://res.cloudinary.com/test/image/upload/autosales-rpa/dashboard_resumen.png"}


class _FakeCloudinary:
    """Fake cloudinary module with config and uploader."""

    configured: dict = {}
    uploader = _FakeUploader()

    @staticmethod
    def config(**kwargs) -> None:  # noqa: ANN003
        _FakeCloudinary.configured = kwargs


def test_upload_dashboard_returns_secure_url(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    dashboard = tmp_path / "dashboard_resumen.png"
    dashboard.write_bytes(b"\x89PNG fake image content")

    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "test_cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "123456")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "secret_abc")
    monkeypatch.setattr("src.infrastructure.uploader.cloudinary", _FakeCloudinary)
    monkeypatch.setattr("src.infrastructure.uploader.cloudinary.uploader", _FakeUploader)

    url = upload_dashboard(dashboard)

    assert url == "https://res.cloudinary.com/test/image/upload/autosales-rpa/dashboard_resumen.png"
    assert _FakeCloudinary.configured["cloud_name"] == "test_cloud"
    assert _FakeCloudinary.configured["secure"] is True
    assert _FakeUploader.last_call_kwargs["overwrite"] is True


def test_upload_dashboard_raises_if_env_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    dashboard = tmp_path / "dashboard_resumen.png"
    dashboard.write_bytes(b"\x89PNG fake image content")

    monkeypatch.delenv("CLOUDINARY_CLOUD_NAME", raising=False)
    monkeypatch.delenv("CLOUDINARY_API_KEY", raising=False)
    monkeypatch.delenv("CLOUDINARY_API_SECRET", raising=False)

    with pytest.raises(EnvironmentError, match="CLOUDINARY_CLOUD_NAME"):
        upload_dashboard(dashboard)


def test_upload_dashboard_raises_if_file_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "test_cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "123456")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "secret_abc")

    with pytest.raises(FileNotFoundError, match="not found"):
        upload_dashboard(tmp_path / "nonexistent.png")
