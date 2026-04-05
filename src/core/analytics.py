"""core/analytics.py – KPI calculations and business logic."""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)

COL_SEDE = "Sede"
COL_MODELO = "MODELO"
COL_CANAL = "Canal"
COL_SEGMENTO = "Segmento"
COL_CLIENTE = "Cliente"
COL_PRECIO = "Precio Venta sin IGV"

REQUIRED_COLUMNS = {
    COL_SEDE,
    COL_MODELO,
    COL_CANAL,
    COL_SEGMENTO,
    COL_CLIENTE,
    COL_PRECIO,
}


def _validate_analytics_columns(df: pd.DataFrame) -> None:
    """Ensure analytics-required columns exist.

    Raises:
        KeyError: If one or more required columns are missing.
    """
    missing = REQUIRED_COLUMNS.difference(set(df.columns))
    if missing:
        missing_fmt = ", ".join(sorted(missing))
        raise KeyError(f"Missing required analytics columns: {missing_fmt}")


def sales_by_sede(df: pd.DataFrame) -> pd.Series:
    """Compute billed amount grouped by sede."""
    _validate_analytics_columns(df)
    return df.groupby(COL_SEDE)[COL_PRECIO].sum().sort_values(ascending=False)


def top_models(df: pd.DataFrame, n: int = 5) -> pd.Series:
    """Compute top-N most frequent vehicle models."""
    _validate_analytics_columns(df)
    return df[COL_MODELO].value_counts().head(n)


def sales_by_canal(df: pd.DataFrame) -> pd.Series:
    """Compute billed amount grouped by canal."""
    _validate_analytics_columns(df)
    return df.groupby(COL_CANAL)[COL_PRECIO].sum().sort_values(ascending=False)


def sales_by_segmento(df: pd.DataFrame) -> pd.Series:
    """Compute distribution of records grouped by segmento."""
    _validate_analytics_columns(df)
    return df[COL_SEGMENTO].value_counts()


def unique_clients(df: pd.DataFrame) -> int:
    """Return number of unique clients."""
    _validate_analytics_columns(df)
    return int(df[COL_CLIENTE].nunique())


def total_sales(df: pd.DataFrame) -> int:
    """Return total number of sales records."""
    _validate_analytics_columns(df)
    return int(df.shape[0])


def total_billed(df: pd.DataFrame) -> float:
    """Return total billed amount (sum of price without IGV)."""
    _validate_analytics_columns(df)
    return float(df[COL_PRECIO].sum())


def compute_all_kpis(df: pd.DataFrame) -> dict[str, pd.Series | int | float]:
    """Compute all mandatory KPIs in one call."""
    logger.info("Computing KPI set.")
    kpis: dict[str, pd.Series | int | float] = {
        "sales_by_sede": sales_by_sede(df),
        "top_models": top_models(df),
        "sales_by_canal": sales_by_canal(df),
        "sales_by_segmento": sales_by_segmento(df),
        "unique_clients": unique_clients(df),
        "total_sales": total_sales(df),
        "total_billed": total_billed(df),
    }
    logger.info(
        "KPIs ready | total_sales=%d | unique_clients=%d | total_billed=%.2f",
        kpis["total_sales"],
        kpis["unique_clients"],
        kpis["total_billed"],
    )
    return kpis
