"""Descriptive statistics and categorical frequency analysis for CSV Explorer.

Provides:
- Robust numeric statistics (mean, median, std, var, min, max, Q1, Q3, IQR, skewness)
- Proper handling of edge cases (constant columns, single observation, zero observations, infs)
- Preserves None/NaN for undefined statistics (never misleadingly replaced with 0)
- Categorical frequency distribution tables with top-N filtering and omission indicators
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np
import pandas as pd


@dataclass
class NumericColumnStats:
    """Statistical summary for a single numeric column."""
    column: str
    count: int
    missing: int
    missing_pct: float
    mean: Optional[float]
    median: Optional[float]
    std: Optional[float]
    variance: Optional[float]
    min: Optional[float]
    max: Optional[float]
    q1: Optional[float]
    q3: Optional[float]
    iqr: Optional[float]
    skewness: Optional[float]


@dataclass
class CategoricalColumnStats:
    """Frequency and cardinality summary for a categorical column."""
    column: str
    total_observations: int
    missing_observations: int
    missing_pct: float
    unique_count: int
    most_frequent_value: Optional[Any]
    most_frequent_count: int
    most_frequent_pct: float
    frequency_table: pd.DataFrame  # Columns: ['Value', 'Count', 'Percentage']
    total_distinct_omitted: int = 0


def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    """Identify strictly numeric columns, excluding booleans.

    Args:
        df: Input DataFrame.

    Returns:
        list[str]: Column names with numeric dtypes.
    """
    numeric_cols = []
    for col in df.columns:
        series = df[col]
        # Exclude boolean dtypes explicitly
        if pd.api.types.is_bool_dtype(series.dtype):
            continue
        if pd.api.types.is_numeric_dtype(series.dtype):
            numeric_cols.append(str(col))
    return numeric_cols


def compute_column_numeric_stats(series: pd.Series, col_name: str) -> NumericColumnStats:
    """Compute detailed descriptive statistics for a single numeric series.

    Guarantees mathematical correctness for edge cases:
    - If valid count == 0: all stats are None.
    - If valid count == 1: std, variance, and skewness are None.
    - If valid count == 2: skewness is None.
    - If variance == 0: skewness is 0.0 or None.
    - Replaces infinite values with NaN before calculating finite statistics.

    Args:
        series: Pandas series containing numeric data.
        col_name: Name of the column.

    Returns:
        NumericColumnStats: Descriptive statistics container.
    """
    total_obs = len(series)
    # Replace positive and negative infinity with NaN for robust calculation
    clean_series = series.replace([np.inf, -np.inf], np.nan).dropna()
    valid_count = len(clean_series)
    missing_count = total_obs - valid_count
    missing_pct = round((missing_count / total_obs * 100.0), 2) if total_obs > 0 else 0.0

    if valid_count == 0:
        return NumericColumnStats(
            column=col_name,
            count=0,
            missing=missing_count,
            missing_pct=missing_pct,
            mean=None,
            median=None,
            std=None,
            variance=None,
            min=None,
            max=None,
            q1=None,
            q3=None,
            iqr=None,
            skewness=None,
        )

    # Basic values
    c_min = float(clean_series.min())
    c_max = float(clean_series.max())
    c_mean = float(clean_series.mean())
    c_median = float(clean_series.median())

    q1_val = float(clean_series.quantile(0.25))
    q3_val = float(clean_series.quantile(0.75))
    iqr_val = float(q3_val - q1_val)

    # Standard deviation & variance (sample-based, ddof=1)
    if valid_count > 1:
        c_std = float(clean_series.std(ddof=1))
        c_var = float(clean_series.var(ddof=1))
    else:
        c_std = None
        c_var = None

    # Skewness requires at least 3 points and non-zero standard deviation
    if valid_count >= 3 and c_std is not None and c_std > 0:
        skew_val = clean_series.skew()
        c_skew = float(skew_val) if not math.isnan(skew_val) else None
    elif valid_count >= 3 and c_std == 0:
        c_skew = 0.0
    else:
        c_skew = None

    return NumericColumnStats(
        column=col_name,
        count=valid_count,
        missing=missing_count,
        missing_pct=missing_pct,
        mean=round(c_mean, 4) if c_mean is not None else None,
        median=round(c_median, 4) if c_median is not None else None,
        std=round(c_std, 4) if c_std is not None else None,
        variance=round(c_var, 4) if c_var is not None else None,
        min=round(c_min, 4) if c_min is not None else None,
        max=round(c_max, 4) if c_max is not None else None,
        q1=round(q1_val, 4) if q1_val is not None else None,
        q3=round(q3_val, 4) if q3_val is not None else None,
        iqr=round(iqr_val, 4) if iqr_val is not None else None,
        skewness=round(c_skew, 4) if c_skew is not None else None,
    )


def get_numeric_statistics(
    df: pd.DataFrame,
    columns: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Generate a descriptive statistics DataFrame for specified or all numeric columns.

    Args:
        df: Input DataFrame.
        columns: Optional list of numeric columns to evaluate. Defaults to all numeric columns.

    Returns:
        pd.DataFrame: Table with columns:
            ['Metric', col1, col2, ...] or indexed by Metric.
    """
    if columns is None:
        target_cols = get_numeric_columns(df)
    else:
        target_cols = [c for c in columns if c in df.columns]

    if not target_cols:
        return pd.DataFrame()

    stats_list = [compute_column_numeric_stats(df[c], c) for c in target_cols]

    metrics = [
        ("Valid Count", lambda s: s.count),
        ("Missing Count", lambda s: s.missing),
        ("Missing %", lambda s: s.missing_pct),
        ("Mean", lambda s: s.mean),
        ("Std Dev", lambda s: s.std),
        ("Variance", lambda s: s.variance),
        ("Minimum", lambda s: s.min),
        ("25% (Q1)", lambda s: s.q1),
        ("50% (Median)", lambda s: s.median),
        ("75% (Q3)", lambda s: s.q3),
        ("Maximum", lambda s: s.max),
        ("IQR", lambda s: s.iqr),
        ("Skewness", lambda s: s.skewness),
    ]

    result_dict: dict[str, Any] = {"Metric": [m[0] for m in metrics]}
    for s in stats_list:
        result_dict[s.column] = [m[1](s) for m in metrics]

    return pd.DataFrame(result_dict)


def get_categorical_statistics(
    df: pd.DataFrame,
    column: str,
    top_n: int = 10,
) -> CategoricalColumnStats:
    """Compute frequency counts and percentages for a single categorical or text column.

    Args:
        df: Input DataFrame.
        column: Categorical column name.
        top_n: Number of most frequent categories to display in the main table.

    Returns:
        CategoricalColumnStats: Cardinality metrics and formatted frequency table.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")

    series = df[column]
    total_obs = len(series)
    missing_obs = int(series.isna().sum())
    missing_pct = round((missing_obs / total_obs * 100.0), 2) if total_obs > 0 else 0.0

    valid_series = series.dropna()
    unique_count = int(valid_series.nunique())

    if unique_count == 0:
        empty_table = pd.DataFrame(columns=["Value", "Count", "Percentage"])
        return CategoricalColumnStats(
            column=column,
            total_observations=total_obs,
            missing_observations=missing_obs,
            missing_pct=missing_pct,
            unique_count=0,
            most_frequent_value=None,
            most_frequent_count=0,
            most_frequent_pct=0.0,
            frequency_table=empty_table,
            total_distinct_omitted=0,
        )

    # Calculate full frequency counts
    value_counts = valid_series.value_counts(dropna=True)
    most_freq_val = value_counts.index[0]
    most_freq_count = int(value_counts.iloc[0])
    most_freq_pct = round((most_freq_count / len(valid_series) * 100.0), 2)

    total_omitted = max(0, unique_count - top_n)
    display_counts = value_counts.head(top_n)

    table_data = []
    for val, count in display_counts.items():
        pct = round((count / len(valid_series) * 100.0), 2)
        table_data.append({
            "Value": str(val),
            "Count": int(count),
            "Percentage": pct,
        })

    freq_df = pd.DataFrame(table_data)

    return CategoricalColumnStats(
        column=column,
        total_observations=total_obs,
        missing_observations=missing_obs,
        missing_pct=missing_pct,
        unique_count=unique_count,
        most_frequent_value=most_freq_val,
        most_frequent_count=most_freq_count,
        most_frequent_pct=most_freq_pct,
        frequency_table=freq_df,
        total_distinct_omitted=total_omitted,
    )
