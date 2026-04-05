"""core/extraction.py – Data ingestion and merge operations.

Loads required Excel sheets and performs a LEFT JOIN between
`Ventas` and `Vehículos` by `ID_Vehículo`.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

SHEET_VENTAS = "Ventas"
SHEET_VEHICULOS = "Vehículos"
JOIN_KEY = "ID_Vehículo"
REQUIRED_VENTAS_COLUMNS = {
    JOIN_KEY,
    "Fecha",
    "Canal",
    "Cliente",
    "Segmento",
    "Precio Venta sin IGV",
    "Sede",
}
REQUIRED_VEHICULOS_COLUMNS = {JOIN_KEY, "MARCA", "MODELO"}


def _validate_required_columns(
    df: pd.DataFrame,
    required_columns: set[str],
    context: str,
) -> None:
    """Validate that *df* contains all *required_columns*.

    Args:
        df: DataFrame to validate.
        required_columns: Set of mandatory column names.
        context: Human-readable source context for error messages.

    Raises:
        KeyError: If any required column is missing.
    """
    missing = required_columns.difference(set(df.columns))
    if missing:
        missing_fmt = ", ".join(sorted(missing))
        raise KeyError(f"Missing columns in {context}: {missing_fmt}")


def load_excel(file_path: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load `Ventas` and `Vehículos` sheets from the Excel source.

    Args:
        file_path: Path to `Ventas Fundamentos.xlsx`.

    Returns:
        Tuple `(ventas_df, vehiculos_df)`.

    Raises:
        FileNotFoundError: If the source file does not exist.
        KeyError: If required columns are missing.
        ValueError: If expected sheets are not present.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {path.resolve()}")

    logger.info("Loading workbook from %s", path.resolve())

    try:
        ventas_df: pd.DataFrame = pd.read_excel(path, sheet_name=SHEET_VENTAS, engine="openpyxl")
        vehiculos_df: pd.DataFrame = pd.read_excel(path, sheet_name=SHEET_VEHICULOS, engine="openpyxl")
    except ValueError:
        logger.exception("Missing expected sheet(s) in workbook.")
        raise
    except Exception:
        logger.exception("Unexpected error while reading Excel workbook.")
        raise

    _validate_required_columns(ventas_df, REQUIRED_VENTAS_COLUMNS, "sheet 'Ventas'")
    _validate_required_columns(vehiculos_df, REQUIRED_VEHICULOS_COLUMNS, "sheet 'Vehículos'")

    logger.info(
        "Workbook loaded: %d ventas rows, %d vehículos rows.",
        len(ventas_df),
        len(vehiculos_df),
    )
    return ventas_df, vehiculos_df


def merge_data(ventas_df: pd.DataFrame, vehiculos_df: pd.DataFrame) -> pd.DataFrame:
    """Merge sales and vehicles datasets by `ID_Vehículo`.

    Args:
        ventas_df: Sales DataFrame.
        vehiculos_df: Vehicle catalog DataFrame.

    Returns:
        Merged DataFrame.

    Raises:
        KeyError: If required columns are missing.
    """
    _validate_required_columns(ventas_df, REQUIRED_VENTAS_COLUMNS, "ventas DataFrame")
    _validate_required_columns(vehiculos_df, REQUIRED_VEHICULOS_COLUMNS, "vehículos DataFrame")

    merged_df = ventas_df.merge(
        vehiculos_df[[JOIN_KEY, "MARCA", "MODELO"]],
        on=JOIN_KEY,
        how="left",
    )

    unmatched_models = int(merged_df["MODELO"].isna().sum())
    if unmatched_models > 0:
        logger.warning(
            "%d sales records could not be matched to a vehicle model.",
            unmatched_models,
        )

    logger.info("Merge complete with %d rows.", len(merged_df))
    return merged_df


def load_and_merge(file_path: str | Path) -> pd.DataFrame:
    """Load Excel data and return merged DataFrame.

    Args:
        file_path: Path to source workbook.

    Returns:
        Merged sales DataFrame.
    """
    ventas_df, vehiculos_df = load_excel(file_path)
    return merge_data(ventas_df, vehiculos_df)
