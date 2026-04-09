"""Tests for src/core/extraction.py."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.core.extraction import load_excel, merge_data


def test_merge_data_keeps_left_join_cardinality(
    sample_ventas_df: pd.DataFrame,
    sample_vehiculos_df: pd.DataFrame,
) -> None:
    merged = merge_data(sample_ventas_df, sample_vehiculos_df)
    assert len(merged) == len(sample_ventas_df)
    assert "MODELO" in merged.columns


def test_merge_data_raises_when_required_column_missing(
    sample_ventas_df: pd.DataFrame,
    sample_vehiculos_df: pd.DataFrame,
) -> None:
    broken_ventas = sample_ventas_df.drop(columns=["Sede"])
    with pytest.raises(KeyError):
        merge_data(broken_ventas, sample_vehiculos_df)


def test_load_excel_raises_file_not_found(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.xlsx"
    with pytest.raises(FileNotFoundError):
        load_excel(missing_file)


def test_load_excel_success(tmp_path: Path) -> None:
    file_path = tmp_path / "Ventas Fundamentos.xlsx"

    ventas = pd.DataFrame(
        {
            "ID_Vehículo": [1],
            "Fecha": pd.to_datetime(["2025-01-01"]),
            "Canal": ["Online"],
            "Cliente": ["Ana"],
            "Segmento": ["Retail"],
            "Precio Venta sin IGV": [10000.0],
            "Sede": ["Lima"],
        }
    )
    vehiculos = pd.DataFrame(
        {
            "ID_Vehículo": [1],
            "MARCA": ["Toyota"],
            "MODELO": ["Yaris"],
        }
    )

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        ventas.to_excel(writer, sheet_name="VENTAS", index=False)
        vehiculos.to_excel(writer, sheet_name="VEHICULOS", index=False)

    import os
    original_sheet_ventas = os.environ.get("SHEET_VENTAS")
    original_sheet_vehiculos = os.environ.get("SHEET_VEHICULOS")
    os.environ["SHEET_VENTAS"] = "VENTAS"
    os.environ["SHEET_VEHICULOS"] = "VEHICULOS"

    try:
        ventas_df, vehiculos_df = load_excel(file_path)
    finally:
        if original_sheet_ventas is None:
            os.environ.pop("SHEET_VENTAS", None)
        else:
            os.environ["SHEET_VENTAS"] = original_sheet_ventas

        if original_sheet_vehiculos is None:
            os.environ.pop("SHEET_VEHICULOS", None)
        else:
            os.environ["SHEET_VEHICULOS"] = original_sheet_vehiculos

    assert not ventas_df.empty
    assert not vehiculos_df.empty


def test_load_excel_canonicalizes_common_alias_columns(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    file_path = tmp_path / "Ventas Fundamentos.xlsx"

    ventas = pd.DataFrame(
        {
            "ID_VEHICULO": [1],
            "FECHA": pd.to_datetime(["2025-01-01"]),
            "CANAL": ["Online"],
            "CLIENTE": ["Ana"],
            "SEGMENTO": ["Retail"],
            "PRECIO VENTA SIN IGV": [10000.0],
            "SEDE": ["Lima"],
        }
    )
    vehiculos = pd.DataFrame(
        {
            "ID_VEHICULO": [1],
            "Marca": ["Toyota"],
            "Modelo": ["Yaris"],
        }
    )

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        ventas.to_excel(writer, sheet_name="VENTAS", index=False)
        vehiculos.to_excel(writer, sheet_name="VEHICULOS", index=False)

    monkeypatch.setenv("SHEET_VENTAS", "VENTAS")
    monkeypatch.setenv("SHEET_VEHICULOS", "VEHICULOS")

    ventas_df, vehiculos_df = load_excel(file_path)

    assert "ID_Vehículo" in ventas_df.columns
    assert "ID_Vehículo" in vehiculos_df.columns
    assert "Precio Venta sin IGV" in ventas_df.columns
