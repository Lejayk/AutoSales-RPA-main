"""Tests for src/core/analytics.py."""

from __future__ import annotations

import pandas as pd
import pytest

from src.core.analytics import (
    compute_all_kpis,
    sales_by_canal,
    sales_by_sede,
    sales_by_segmento,
    top_models,
    total_billed,
    total_sales,
    unique_clients,
)


def test_sales_by_sede(merged_df: pd.DataFrame) -> None:
    result = sales_by_sede(merged_df)
    assert float(result.loc["Lima"]) == 50000.0
    assert float(result.loc["Cusco"]) == 20000.0


def test_top_models_default_top5(merged_df: pd.DataFrame) -> None:
    result = top_models(merged_df)
    assert result.iloc[0] == 2


def test_sales_by_canal(merged_df: pd.DataFrame) -> None:
    result = sales_by_canal(merged_df)
    assert float(result.loc["Online"]) == 25000.0


def test_sales_by_segmento(merged_df: pd.DataFrame) -> None:
    result = sales_by_segmento(merged_df)
    assert int(result.loc["Retail"]) == 3
    assert int(result.loc["Corporate"]) == 2


def test_scalar_metrics(merged_df: pd.DataFrame) -> None:
    assert unique_clients(merged_df) == 4
    assert total_sales(merged_df) == 5
    assert total_billed(merged_df) == 70000.0


def test_compute_all_kpis_has_all_keys(merged_df: pd.DataFrame) -> None:
    kpis = compute_all_kpis(merged_df)
    expected_keys = {
        "sales_by_sede",
        "top_models",
        "sales_by_canal",
        "sales_by_segmento",
        "unique_clients",
        "total_sales",
        "total_billed",
    }
    assert set(kpis.keys()) == expected_keys


def test_analytics_raises_on_missing_columns(merged_df: pd.DataFrame) -> None:
    broken_df = merged_df.drop(columns=["Canal"])
    with pytest.raises(KeyError):
        sales_by_canal(broken_df)
