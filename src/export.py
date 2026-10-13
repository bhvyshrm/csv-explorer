"""Export functionality for Analytix.

Generates:
- Standardized, downloadable CSV bytes for tables (overview, quality, stats, outliers)
- Consolidated JSON analytical report with safe serialization of non-finite values (NaN, Inf)
- Guarantees data privacy: never embeds the entire raw uploaded dataset or local paths
- Captures dataset format and active worksheet metadata for Excel workbooks
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

import numpy as np
import pandas as pd


def export_dataframe_to_csv(df: pd.DataFrame, index: bool = False) -> bytes:
    """Serialize a pandas DataFrame into UTF-8 encoded CSV bytes.

    Args:
        df: Input DataFrame.
        index: Whether to include the row index in the CSV output.

    Returns:
        bytes: UTF-8 encoded CSV content.
    """
    if df is None or (df.empty and len(df.columns) == 0):
        return b""
    return df.to_csv(index=index).encode("utf-8")


def _sanitize_for_json(obj: Any) -> Any:
    """Recursively convert NumPy scalars, NaNs, and timestamps into JSON-compliant types.

    Args:
        obj: Arbitrary Python object.

    Returns:
        Any: JSON-safe primitive (int, float, str, bool, list, dict, None).
    """
    if obj is None:
        return None
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    if isinstance(obj, (list, tuple, set)):
        return [_sanitize_for_json(item) for item in obj]
    if isinstance(obj, dict):
        return {str(k): _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, pd.DataFrame):
        return [_sanitize_for_json(row) for row in obj.to_dict(orient="records")]
    if isinstance(obj, pd.Series):
        return _sanitize_for_json(obj.to_dict())
    return str(obj)


def generate_json_report(
    filename: str,
    overview_dict: dict[str, Any],
    column_metadata_df: Optional[pd.DataFrame] = None,
    quality_summary_dict: Optional[dict[str, Any]] = None,
    numeric_stats_df: Optional[pd.DataFrame] = None,
    outliers_dict: Optional[dict[str, Any]] = None,
    dataset_format: str = "CSV",
    active_worksheet: Optional[str] = None,
) -> str:
    """Assemble a consolidated JSON EDA report and serialize safely.

    Args:
        filename: Name of the uploaded dataset file.
        overview_dict: Dataset dimensions and type metrics.
        column_metadata_df: Column metadata table.
        quality_summary_dict: Quality assessment diagnostics.
        numeric_stats_df: Descriptive statistics table.
        outliers_dict: Outlier summaries for evaluated columns.
        dataset_format: Source file format ('CSV' or 'Excel').
        active_worksheet: Selected worksheet name for Excel files.

    Returns:
        str: Pretty-printed, valid JSON string.
    """
    report_data: dict[str, Any] = {
        "application": "Analytix",
        "version": "2.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_name": filename,
        "dataset_format": dataset_format,
        "overview": overview_dict,
    }

    if active_worksheet:
        report_data["active_worksheet"] = active_worksheet

    if column_metadata_df is not None and not column_metadata_df.empty:
        report_data["columns"] = column_metadata_df.to_dict(orient="records")

    if quality_summary_dict is not None:
        report_data["data_quality"] = quality_summary_dict

    if numeric_stats_df is not None and not numeric_stats_df.empty:
        report_data["numeric_statistics"] = numeric_stats_df.to_dict(orient="records")

    if outliers_dict is not None:
        report_data["outliers"] = outliers_dict

    sanitized_report = _sanitize_for_json(report_data)
    return json.dumps(sanitized_report, indent=2, ensure_ascii=False)
