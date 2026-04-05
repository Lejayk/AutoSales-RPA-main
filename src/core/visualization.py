"""core/visualization.py – Executive dashboard generation."""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

# Non-interactive backend for server/batch execution
matplotlib.use("Agg")

logger = logging.getLogger(__name__)


def build_dashboard(
    sales_by_sede: pd.Series,
    top_models: pd.Series,
    sales_by_segmento: pd.Series,
    sales_by_canal: pd.Series,
    output_path: str | Path,
    style: str = "seaborn-v0_8",
) -> Path:
    """Build a 2x2 KPI dashboard and save as PNG.

    Layout:
        [0,0] Barras: Ventas por Sede
        [0,1] Barras H: Top 5 Modelos
        [1,0] Pie: Segmentación por Segmento
        [1,1] Barras: Ventas por Canal
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with plt.style.context(style):
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("AutoSales-RPA — Dashboard Resumen", fontsize=16, fontweight="bold")

        ax00 = axes[0, 0]
        sales_by_sede.plot(kind="bar", ax=ax00, color="steelblue", edgecolor="white")
        ax00.set_title("Ventas por Sede")
        ax00.set_xlabel("Sede")
        ax00.set_ylabel("Facturación (sin IGV)")
        ax00.tick_params(axis="x", rotation=45)
        _add_value_labels(ax00, orientation="vertical", fmt="{:,.0f}")

        ax01 = axes[0, 1]
        top_models.sort_values().plot(kind="barh", ax=ax01, color="darkorange", edgecolor="white")
        ax01.set_title("Top 5 Modelos más Vendidos")
        ax01.set_xlabel("Unidades")
        ax01.set_ylabel("Modelo")
        _add_value_labels(ax01, orientation="horizontal", fmt="{:.0f}")

        ax10 = axes[1, 0]
        sales_by_segmento.plot(
            kind="pie",
            ax=ax10,
            autopct="%1.1f%%",
            startangle=90,
            colors=plt.cm.Set3.colors,  # type: ignore[attr-defined]
        )
        ax10.set_title("Distribución por Segmento")
        ax10.set_ylabel("")

        ax11 = axes[1, 1]
        sales_by_canal.plot(kind="bar", ax=ax11, color="seagreen", edgecolor="white")
        ax11.set_title("Ventas por Canal")
        ax11.set_xlabel("Canal")
        ax11.set_ylabel("Facturación (sin IGV)")
        ax11.tick_params(axis="x", rotation=45)
        _add_value_labels(ax11, orientation="vertical", fmt="{:,.0f}")

        plt.tight_layout()
        fig.savefig(output, dpi=150, bbox_inches="tight")
        plt.close(fig)

    logger.info("Dashboard saved: %s", output.resolve())
    return output.resolve()


def _add_value_labels(ax: plt.Axes, orientation: str, fmt: str) -> None:
    """Add numeric labels to bars."""
    for patch in ax.patches:
        if orientation == "vertical":
            value = patch.get_height()
            x = patch.get_x() + patch.get_width() / 2
            y = value
            ha, va = "center", "bottom"
        else:
            value = patch.get_width()
            x = value
            y = patch.get_y() + patch.get_height() / 2
            ha, va = "left", "center"

        ax.annotate(fmt.format(value), (x, y), ha=ha, va=va, fontsize=8)
