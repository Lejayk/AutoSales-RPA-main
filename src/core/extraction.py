"""core/extraction.py – Data ingestion and merge operations.

Loads required Excel sheets and performs a LEFT JOIN between
`Ventas` and `Vehículos` by `ID_Vehículo`.
"""

from __future__ import annotations

import logging
import os
import unicodedata
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

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

VENTAS_COLUMN_ALIASES: dict[str, set[str]] = {
    JOIN_KEY: {"ID_VEHICULO", "ID VEHICULO", "IdVehiculo", "idvehiculo"},
    "Fecha": {"FECHA", "Fecha Venta", "Fecha de Venta"},
    "Canal": {"CANAL", "Canal Venta", "Canal de Venta"},
    "Cliente": {"CLIENTE", "Nombre Cliente", "Cliente Nombre"},
    "Segmento": {"SEGMENTO", "Segmento Mercado", "Segmento de Mercado"},
    "Precio Venta sin IGV": {
        "PRECIO VENTA SIN IGV",
        "Precio Venta",
        "Monto Venta",
        "Total Venta",
    },
    "Sede": {"SEDE", "Sucursal", "Tienda"},
}

VEHICULOS_COLUMN_ALIASES: dict[str, set[str]] = {
    JOIN_KEY: {"ID_VEHICULO", "ID VEHICULO", "IdVehiculo", "idvehiculo"},
    "MARCA": {"Marca", "marca"},
    "MODELO": {"Modelo", "modelo", "Modelo Vehiculo", "Modelo Vehículo"},
}


def _sheet_name(env_var: str, default: str) -> str:
    """Resolve sheet name from env var with default fallback."""
    value = os.getenv(env_var, "").strip()
    return value or default


def _normalized_label(label: str) -> str:
    """Normalize labels for resilient matching.

    Normalization removes accents, whitespace and non-alphanumeric chars,
    then lowercases the string.
    """
    ascii_label = "".join(
        char
        for char in unicodedata.normalize("NFKD", str(label))
        if not unicodedata.combining(char)
    )
    return "".join(char for char in ascii_label.lower() if char.isalnum())


def _canonicalize_columns(
    df: pd.DataFrame,
    required_columns: set[str],
    aliases: dict[str, set[str]],
    context: str,
) -> pd.DataFrame:
    """Rename input columns to canonical names using robust alias matching.

    Raises:
        KeyError: If required canonical columns cannot be uniquely resolved.
    """
    source_columns = [str(col).strip() for col in df.columns]
    normalized_to_sources: dict[str, list[str]] = {}
    for col in source_columns:
        normalized_to_sources.setdefault(_normalized_label(col), []).append(col)

    rename_map: dict[str, str] = {}
    missing: list[str] = []
    ambiguous: list[str] = []

    for required in sorted(required_columns):
        # If canonical column already exists, keep it as source of truth.
        if required in source_columns:
            continue

        candidate_labels = {required, *aliases.get(required, set())}
        candidate_keys = {_normalized_label(label) for label in candidate_labels}

        matches: list[str] = []
        for key in candidate_keys:
            matches.extend(normalized_to_sources.get(key, []))

        # Keep stable uniqueness while preserving order.
        unique_matches: list[str] = list(dict.fromkeys(matches))

        if not unique_matches:
            accepted = ", ".join(sorted(candidate_labels))
            missing.append(f"{required} (aliases: {accepted})")
            continue

        if len(unique_matches) > 1:
            ambiguous.append(f"{required} -> {unique_matches}")
            continue

        rename_map[unique_matches[0]] = required

    if ambiguous:
        raise KeyError(
            f"Ambiguous columns in {context}: " + "; ".join(ambiguous)
        )

    if missing:
        available = ", ".join(source_columns)
        raise KeyError(
            f"Missing columns in {context}: {'; '.join(missing)}. "
            f"Available columns: {available}"
        )

    if rename_map:
        logger.info("Canonicalizing columns for %s: %s", context, rename_map)
        return df.rename(columns=rename_map)

    return df


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

    sheet_ventas = _sheet_name("SHEET_VENTAS", "Ventas")
    sheet_vehiculos = _sheet_name("SHEET_VEHICULOS", "Vehículos")

    try:
        ventas_df: pd.DataFrame = pd.read_excel(path, sheet_name=sheet_ventas, engine="openpyxl")
        vehiculos_df: pd.DataFrame = pd.read_excel(path, sheet_name=sheet_vehiculos, engine="openpyxl")
    except ValueError:
        logger.exception(
            "Missing expected sheet(s) in workbook. "
            "Configured sheets: SHEET_VENTAS='%s', SHEET_VEHICULOS='%s'.",
            sheet_ventas,
            sheet_vehiculos,
        )
        raise
    except Exception:
        logger.exception("Unexpected error while reading Excel workbook.")
        raise

    ventas_df = _canonicalize_columns(
        ventas_df,
        REQUIRED_VENTAS_COLUMNS,
        VENTAS_COLUMN_ALIASES,
        f"sheet '{sheet_ventas}'",
    )
    vehiculos_df = _canonicalize_columns(
        vehiculos_df,
        REQUIRED_VEHICULOS_COLUMNS,
        VEHICULOS_COLUMN_ALIASES,
        f"sheet '{sheet_vehiculos}'",
    )

    _validate_required_columns(ventas_df, REQUIRED_VENTAS_COLUMNS, f"sheet '{sheet_ventas}'")
    _validate_required_columns(vehiculos_df, REQUIRED_VEHICULOS_COLUMNS, f"sheet '{sheet_vehiculos}'")

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
