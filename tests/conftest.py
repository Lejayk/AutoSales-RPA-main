"""Shared fixtures for AutoSales-RPA tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def sample_ventas_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ID_Vehículo": [1, 2, 3, 2, 4],
            "Fecha": pd.to_datetime([
                "2025-01-10",
                "2025-01-11",
                "2025-01-12",
                "2025-01-12",
                "2025-01-13",
            ]),
            "Canal": ["Online", "Showroom", "Online", "Flota", "Showroom"],
            "Cliente": ["Ana", "Luis", "Ana", "Marta", "Pedro"],
            "Segmento": ["Retail", "Retail", "Corporate", "Corporate", "Retail"],
            "Precio Venta sin IGV": [10000.0, 20000.0, 15000.0, 20000.0, 5000.0],
            "Sede": ["Lima", "Lima", "Cusco", "Lima", "Cusco"],
        }
    )


@pytest.fixture
def sample_vehiculos_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ID_Vehículo": [1, 2, 3],
            "MARCA": ["Toyota", "Kia", "Hyundai"],
            "MODELO": ["Yaris", "Rio", "Accent"],
        }
    )


@pytest.fixture
def merged_df(sample_ventas_df: pd.DataFrame, sample_vehiculos_df: pd.DataFrame) -> pd.DataFrame:
    return sample_ventas_df.merge(
        sample_vehiculos_df[["ID_Vehículo", "MARCA", "MODELO"]],
        on="ID_Vehículo",
        how="left",
    )


@pytest.fixture
def output_dashboard_path(tmp_path: Path) -> Path:
    return tmp_path / "dashboard_resumen.png"
