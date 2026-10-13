"""Interquartile Range (IQR) outlier detection for CSV Explorer.

Implements the standard statistical IQR rule:
- Q1 = 25th percentile
- Q3 = 75th percentile
- IQR = Q3 - Q1
- Lower Bound = Q1 - 1.5 * IQR
- Upper Bound = Q3 + 1.5 * IQR

A value is flagged as an outlier if:
    value < Lower Bound OR value > Upper Bound

Guarantees:
- Never modifies the original DataFrame.
- Correctly handles nulls, constant columns, and edge cases.
- Provides flagged subset, bounds, counts, and percentages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class OutlierResult:
    """Detailed container holding IQR outlier detection metrics."""
    column: str
    q1: Optional[float]
    q3: Optional[float]
    iqr: Optional[float]
    multiplier: float
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    valid_observations_count: int
    flagged_count: int
    flagged_pct: float
    lower_outliers_count: int
    upper_outliers_count: int
    flagged_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    status_message: str = ""


def detect_outliers_iqr(
    df: pd.DataFrame,
    column: str,
    multiplier: float = 1.5,
) -> OutlierResult:
    """Detect outliers in a numeric column using the Interquartile Range (IQR) rule.

    Calculates quartiles on valid non-null observations without altering the
    original DataFrame.

    Args:
        df: Input DataFrame.
        column: Numeric column name.
        multiplier: IQR multiplier (standard 1.5 for moderate outliers, 3.0 for extreme).

    Returns:
        OutlierResult: Statistical boundaries, outlier counts, and preview slice.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

    series = df[column]
    # Filter to finite numeric observations
    clean_series = series.replace([np.inf, -np.inf], np.nan).dropna()
    valid_count = len(clean_series)

    if valid_count < 4:
        return OutlierResult(
            column=column,
            q1=None,
            q3=None,
            iqr=None,
            multiplier=multiplier,
            lower_bound=None,
            upper_bound=None,
            valid_observations_count=valid_count,
            flagged_count=0,
            flagged_pct=0.0,
            lower_outliers_count=0,
            upper_outliers_count=0,
            flagged_df=pd.DataFrame(columns=df.columns),
            status_message=(
                f"Insufficient valid observations ({valid_count}). "
                "At least 4 observations are required for meaningful quartile calculation."
            ),
        )

    q1_val = float(clean_series.quantile(0.25))
    q3_val = float(clean_series.quantile(0.75))
    iqr_val = float(q3_val - q1_val)

    lower_bound = float(q1_val - multiplier * iqr_val)
    upper_bound = float(q3_val + multiplier * iqr_val)

    # Boolean masks for original dataframe rows
    # Missing values evaluate to False in numeric comparisons
    lower_mask = df[column] < lower_bound
    upper_mask = df[column] > upper_bound
    outlier_mask = lower_mask | upper_mask

    lower_count = int(lower_mask.sum())
    upper_count = int(upper_mask.sum())
    total_flagged = int(outlier_mask.sum())
    flagged_pct = round((total_flagged / valid_count * 100.0), 2) if valid_count > 0 else 0.0

    # Extract non-destructive copy of flagged rows
    flagged_slice = df[outlier_mask].copy()

    if iqr_val == 0.0:
        status_message = (
            "Notice: IQR is 0.0 (identical 25th and 75th percentiles). "
            "Any values diverging from this central value were flagged by the standard formula."
        )
    elif total_flagged == 0:
        status_message = "No observations fall outside the calculated IQR boundaries."
    else:
        status_message = (
            f"Detected {total_flagged:,} potential outlier(s) "
            f"({lower_count:,} below {lower_bound:.2f}, {upper_count:,} above {upper_bound:.2f})."
        )

    return OutlierResult(
        column=column,
        q1=round(q1_val, 4),
        q3=round(q3_val, 4),
        iqr=round(iqr_val, 4),
        multiplier=multiplier,
        lower_bound=round(lower_bound, 4),
        upper_bound=round(upper_bound, 4),
        valid_observations_count=valid_count,
        flagged_count=total_flagged,
        flagged_pct=flagged_pct,
        lower_outliers_count=lower_count,
        upper_outliers_count=upper_count,
        flagged_df=flagged_slice,
        status_message=status_message,
    )
