"""Dataset structural overview, column classification, and metadata generation.

Calculates key dataset metrics:
- Dimension counts (rows, columns, total cells)
- Memory usage with human-readable formatting
- Type breakdowns (numeric, categorical, datetime, boolean)
- Column-level metadata tables (null counts, unique counts, inferred types)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class DatasetOverview:
    """Structured container holding high-level dataset metrics."""
    total_rows: int
    total_columns: int
    total_cells: int
    memory_usage_bytes: int
    memory_usage_formatted: str
    numeric_columns: list[str] = field(default_factory=list)
    categorical_columns: list[str] = field(default_factory=list)
    datetime_columns: list[str] = field(default_factory=list)
    boolean_columns: list[str] = field(default_factory=list)
    other_columns: list[str] = field(default_factory=list)
    total_missing_cells: int = 0
    missing_cells_pct: float = 0.0
    total_duplicate_rows: int = 0
    duplicate_rows_pct: float = 0.0


def format_bytes(num_bytes: int) -> str:
    """Convert an integer byte count into a readable string (B, KB, MB, GB).

    Args:
        num_bytes: Size in bytes.

    Returns:
        str: Formatted string (e.g. '12.4 KB', '1.2 MB').
    """
    if num_bytes < 1024:
        return f"{num_bytes} B"
    for unit in ["KB", "MB", "GB", "TB"]:
        num_bytes /= 1024.0
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
    return f"{num_bytes:.2f} PB"


def classify_columns(df: pd.DataFrame) -> dict[str, list[str]]:
    """Classify DataFrame columns into semantic data categories.

    Distinguishes numeric (int, float) from boolean, datetime, and categorical/text.

    Args:
        df: Input DataFrame.

    Returns:
        dict[str, list[str]]: Dictionary with keys:
            'numeric', 'categorical', 'datetime', 'boolean', 'other'.
    """
    categories: dict[str, list[str]] = {
        "numeric": [],
        "categorical": [],
        "datetime": [],
        "boolean": [],
        "other": [],
    }

    for col in df.columns:
        series = df[col]
        dtype = series.dtype

        # 1. Boolean check (must precede numeric check because bool is a subclass of int in python/numpy)
        if pd.api.types.is_bool_dtype(dtype):
            categories["boolean"].append(col)
        # 2. Datetime check
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            categories["datetime"].append(col)
        # 3. Numeric check (integers and floats)
        elif pd.api.types.is_numeric_dtype(dtype):
            categories["numeric"].append(col)
        # 4. Categorical / string / object check
        elif pd.api.types.is_string_dtype(dtype) or pd.api.types.is_object_dtype(dtype) or isinstance(dtype, pd.CategoricalDtype):
            categories["categorical"].append(col)
        else:
            categories["other"].append(col)

    return categories


def get_dataset_overview(df: pd.DataFrame) -> DatasetOverview:
    """Compute high-level summary metrics for a dataset.

    Args:
        df: Input pandas DataFrame.

    Returns:
        DatasetOverview: Dataclass containing dimension and type metrics.
    """
    total_rows = len(df)
    total_columns = len(df.columns)
    total_cells = total_rows * total_columns

    memory_bytes = int(df.memory_usage(deep=True).sum()) if not df.empty else 0
    formatted_mem = format_bytes(memory_bytes)

    classified = classify_columns(df)

    if total_cells > 0:
        total_missing = int(df.isna().sum().sum())
        missing_pct = round((total_missing / total_cells) * 100.0, 2)
    else:
        total_missing = 0
        missing_pct = 0.0

    if total_rows > 0:
        total_dups = int(df.duplicated().sum())
        dups_pct = round((total_dups / total_rows) * 100.0, 2)
    else:
        total_dups = 0
        dups_pct = 0.0

    return DatasetOverview(
        total_rows=total_rows,
        total_columns=total_columns,
        total_cells=total_cells,
        memory_usage_bytes=memory_bytes,
        memory_usage_formatted=formatted_mem,
        numeric_columns=classified["numeric"],
        categorical_columns=classified["categorical"],
        datetime_columns=classified["datetime"],
        boolean_columns=classified["boolean"],
        other_columns=classified["other"],
        total_missing_cells=total_missing,
        missing_cells_pct=missing_pct,
        total_duplicate_rows=total_dups,
        duplicate_rows_pct=dups_pct,
    )


def get_column_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """Generate a detailed metadata table for every column in the dataset.

    Args:
        df: Input DataFrame.

    Returns:
        pd.DataFrame: Table with column names, inferred types, null counts,
                      percentages, and unique counts.
    """
    if df.empty and len(df.columns) == 0:
        return pd.DataFrame(
            columns=[
                "Column Name",
                "Inferred Type",
                "Pandas Dtype",
                "Non-Null Count",
                "Missing Count",
                "Missing %",
                "Unique Values",
            ]
        )

    classified = classify_columns(df)
    type_map = {}
    for col in classified["numeric"]:
        type_map[col] = "Numeric"
    for col in classified["categorical"]:
        type_map[col] = "Categorical"
    for col in classified["datetime"]:
        type_map[col] = "Datetime"
    for col in classified["boolean"]:
        type_map[col] = "Boolean"
    for col in classified["other"]:
        type_map[col] = "Other"

    rows = []
    total_rows = len(df)

    for col in df.columns:
        series = df[col]
        missing_count = int(series.isna().sum())
        non_null_count = total_rows - missing_count
        missing_pct = round((missing_count / total_rows * 100.0), 2) if total_rows > 0 else 0.0
        unique_count = int(series.nunique(dropna=True))

        rows.append({
            "Column Name": str(col),
            "Inferred Type": type_map.get(col, "Unknown"),
            "Pandas Dtype": str(series.dtype),
            "Non-Null Count": non_null_count,
            "Missing Count": missing_count,
            "Missing %": missing_pct,
            "Unique Values": unique_count,
        })

    return pd.DataFrame(rows)


def get_column_sample_values(df: pd.DataFrame, col: str, n_samples: int = 5) -> list[Any]:
    """Retrieve up to n_samples representative non-null values for a column.

    Args:
        df: Input DataFrame.
        col: Target column name.
        n_samples: Number of sample values to return.

    Returns:
        list[Any]: List of representative values.
    """
    if col not in df.columns:
        return []
    valid_series = df[col].dropna()
    if valid_series.empty:
        return []
    return valid_series.head(n_samples).tolist()
