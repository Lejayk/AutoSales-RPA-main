"""Tests for src/core/visualization.py."""

from __future__ import annotations

import pandas as pd

from src.core.visualization import build_dashboard


def test_build_dashboard_creates_png(
    merged_df: pd.DataFrame,
    output_dashboard_path,
) -> None:
    sales_by_sede = merged_df.groupby("Sede")["Precio Venta sin IGV"].sum()
    top_models = merged_df["MODELO"].fillna("Sin modelo").value_counts().head(5)
    sales_by_segmento = merged_df["Segmento"].value_counts()
    sales_by_canal = merged_df.groupby("Canal")["Precio Venta sin IGV"].sum()

    saved_path = build_dashboard(
        sales_by_sede=sales_by_sede,
        top_models=top_models,
        sales_by_segmento=sales_by_segmento,
        sales_by_canal=sales_by_canal,
        output_path=output_dashboard_path,
        style="seaborn-v0_8",
    )

    assert saved_path.exists()
    assert saved_path.suffix == ".png"
