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
        ventas.to_excel(writer, sheet_name="Ventas", index=False)
        vehiculos.to_excel(writer, sheet_name="Vehículos", index=False)

    ventas_df, vehiculos_df = load_excel(file_path)
    assert not ventas_df.empty
    assert not vehiculos_df.empty
