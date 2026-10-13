"""Data quality assessment module for CSV Explorer.

Performs deterministic diagnostic checks:
- Missing value analysis (per column and dataset-wide)
- Duplicate row detection and preview extraction
- Constant column identification (excluding fully null columns)
- Empty and nearly-empty column detection with configurable threshold
- Transparent, heuristic-based data quality summary
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import pandas as pd


class IssueSeverity(str, Enum):
    """Severity classification for detected data quality issues."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class QualityIssue:
    """Diagnostic issue container."""
    title: str
    description: str
    severity: IssueSeverity
    affected_columns: list[str] = field(default_factory=list)


@dataclass
class MissingValueSummary:
    """Summary of missing value metrics across the dataset."""
    total_missing_cells: int
    missing_cells_pct: float
    columns_with_missing_count: int
    detail_table: pd.DataFrame  # Columns: ['Column', 'Missing Count', 'Missing %', 'Non-Missing Count']


@dataclass
class DuplicateSummary:
    """Summary of duplicated rows in the dataset."""
    total_duplicates: int
    duplicate_pct: float
    rows_remaining_after_dedup: int
    duplicate_rows_preview: pd.DataFrame


@dataclass
class ColumnVarianceSummary:
    """Summary of constant, empty, and nearly empty columns."""
    constant_columns: dict[str, Any]  # col -> single distinct value
    entirely_empty_columns: list[str]
    nearly_empty_columns: list[str]  # col with missing_pct >= threshold and < 100%
    threshold_pct: float


@dataclass
class DataQualityReport:
    """Comprehensive data quality evaluation container."""
    status: str  # "No major issues detected", "Some issues need attention", "Several data quality issues detected"
    overall_health_score: float  # 0 to 100 transparent heuristic
    issues: list[QualityIssue]
    missing_summary: MissingValueSummary
    duplicate_summary: DuplicateSummary
    variance_summary: ColumnVarianceSummary


def analyze_missing_values(df: pd.DataFrame) -> MissingValueSummary:
    """Calculate column-wise and global missing value counts and percentages.

    Args:
        df: Input DataFrame.

    Returns:
        MissingValueSummary: Detailed metrics table and aggregate statistics.
    """
    total_rows = len(df)
    total_cells = total_rows * len(df.columns)

    if total_rows == 0 or len(df.columns) == 0:
        empty_table = pd.DataFrame(
            columns=["Column", "Missing Count", "Missing %", "Non-Missing Count"]
        )
        return MissingValueSummary(
            total_missing_cells=0,
            missing_cells_pct=0.0,
            columns_with_missing_count=0,
            detail_table=empty_table,
        )

    rows = []
    total_missing = 0
    cols_with_missing = 0

    for col in df.columns:
        missing_count = int(df[col].isna().sum())
        non_missing_count = total_rows - missing_count
        missing_pct = round((missing_count / total_rows) * 100.0, 2)

        total_missing += missing_count
        if missing_count > 0:
            cols_with_missing += 1

        rows.append({
            "Column": str(col),
            "Missing Count": missing_count,
            "Missing %": missing_pct,
            "Non-Missing Count": non_missing_count,
        })

    detail_table = pd.DataFrame(rows).sort_values(by="Missing Count", ascending=False).reset_index(drop=True)
    global_missing_pct = round((total_missing / total_cells) * 100.0, 2) if total_cells > 0 else 0.0

    return MissingValueSummary(
        total_missing_cells=total_missing,
        missing_cells_pct=global_missing_pct,
        columns_with_missing_count=cols_with_missing,
        detail_table=detail_table,
    )


def analyze_duplicates(df: pd.DataFrame, max_preview: int = 20) -> DuplicateSummary:
    """Identify duplicate rows and extract an inspection preview.

    Args:
        df: Input DataFrame.
        max_preview: Maximum duplicate rows to include in preview.

    Returns:
        DuplicateSummary: Metrics and preview table.
    """
    total_rows = len(df)
    if total_rows == 0:
        return DuplicateSummary(
            total_duplicates=0,
            duplicate_pct=0.0,
            rows_remaining_after_dedup=0,
            duplicate_rows_preview=pd.DataFrame(columns=df.columns),
        )

    duplicate_mask = df.duplicated(keep="first")
    total_dups = int(duplicate_mask.sum())
    dup_pct = round((total_dups / total_rows) * 100.0, 2)
    remaining_rows = total_rows - total_dups

    # Extract all copies of duplicate rows so the user can see both original and duplicate
    if total_dups > 0:
        all_duplicate_copies = df[df.duplicated(keep=False)].head(max_preview)
    else:
        all_duplicate_copies = pd.DataFrame(columns=df.columns)

    return DuplicateSummary(
        total_duplicates=total_dups,
        duplicate_pct=dup_pct,
        rows_remaining_after_dedup=remaining_rows,
        duplicate_rows_preview=all_duplicate_copies,
    )


def analyze_column_variance(
    df: pd.DataFrame,
    nearly_empty_threshold_pct: float = 90.0,
) -> ColumnVarianceSummary:
    """Detect constant columns, entirely empty columns, and nearly empty columns.

    Args:
        df: Input DataFrame.
        nearly_empty_threshold_pct: Percentage threshold above which a column is
                                     flagged as nearly empty (default 90.0%).

    Returns:
        ColumnVarianceSummary: Categorization of constant and sparse columns.
    """
    total_rows = len(df)
    constant_columns: dict[str, Any] = {}
    entirely_empty_columns: list[str] = []
    nearly_empty_columns: list[str] = []

    if total_rows == 0:
        return ColumnVarianceSummary(
            constant_columns={},
            entirely_empty_columns=[],
            nearly_empty_columns=[],
            threshold_pct=nearly_empty_threshold_pct,
        )

    for col in df.columns:
        series = df[col]
        missing_count = int(series.isna().sum())
        non_null_count = total_rows - missing_count
        missing_pct = (missing_count / total_rows) * 100.0

        if non_null_count == 0:
            entirely_empty_columns.append(str(col))
        elif missing_pct >= nearly_empty_threshold_pct:
            nearly_empty_columns.append(str(col))
        else:
            # Check if all non-null values are identical (constant column)
            if series.dropna().nunique() == 1:
                val = series.dropna().iloc[0]
                constant_columns[str(col)] = val

    return ColumnVarianceSummary(
        constant_columns=constant_columns,
        entirely_empty_columns=entirely_empty_columns,
        nearly_empty_columns=nearly_empty_columns,
        threshold_pct=nearly_empty_threshold_pct,
    )


def generate_data_quality_report(
    df: pd.DataFrame,
    nearly_empty_threshold_pct: float = 90.0,
) -> DataQualityReport:
    """Generate a comprehensive, transparent data quality assessment.

    Evaluates:
    - Missing cells count and percentage
    - Duplicate rows
    - Entirely empty columns
    - Nearly empty columns
    - Constant columns

    Computes an explicit health score based on penalties:
    - Base score = 100
    - Missing cells: -1 point per 2% global missing (up to -30)
    - Duplicate rows: -1 point per 2% duplicate rows (up to -25)
    - Constant columns: -5 points per constant column (up to -15)
    - Nearly empty columns: -10 points per column (up to -20)
    - Entirely empty columns: -15 points per column (up to -30)
    - Score bounded between [0, 100].

    Status thresholds:
    - >= 85: "No major issues detected"
    - 65 - 84: "Some issues need attention"
    - < 65: "Several data quality issues detected"

    Args:
        df: Input DataFrame.
        nearly_empty_threshold_pct: Configurable threshold for nearly empty columns.

    Returns:
        DataQualityReport: Comprehensive evaluation object.
    """
    missing_summary = analyze_missing_values(df)
    duplicate_summary = analyze_duplicates(df)
    variance_summary = analyze_column_variance(df, nearly_empty_threshold_pct)

    issues: list[QualityIssue] = []
    penalties = 0.0

    # 1. Evaluate entirely empty columns
    if variance_summary.entirely_empty_columns:
        count = len(variance_summary.entirely_empty_columns)
        penalties += min(count * 15.0, 30.0)
        issues.append(
            QualityIssue(
                title=f"{count} Entirely Empty Column{'s' if count > 1 else ''}",
                description="Column contains 100% missing values and carries no information.",
                severity=IssueSeverity.CRITICAL,
                affected_columns=variance_summary.entirely_empty_columns,
            )
        )

    # 2. Evaluate nearly empty columns
    if variance_summary.nearly_empty_columns:
        count = len(variance_summary.nearly_empty_columns)
        penalties += min(count * 10.0, 20.0)
        issues.append(
            QualityIssue(
                title=f"{count} Nearly Empty Column{'s' if count > 1 else ''}",
                description=(
                    f"Over {nearly_empty_threshold_pct:.0f}% of values are missing. "
                    "Consider whether this column is reliable for analytical modeling."
                ),
                severity=IssueSeverity.WARNING,
                affected_columns=variance_summary.nearly_empty_columns,
            )
        )

    # 3. Evaluate constant columns
    if variance_summary.constant_columns:
        count = len(variance_summary.constant_columns)
        penalties += min(count * 5.0, 15.0)
        col_names = list(variance_summary.constant_columns.keys())
        issues.append(
            QualityIssue(
                title=f"{count} Constant Column{'s' if count > 1 else ''}",
                description="Column contains only one distinct non-null value and offers zero analytical variance.",
                severity=IssueSeverity.INFO,
                affected_columns=col_names,
            )
        )

    # 4. Evaluate duplicate rows
    if duplicate_summary.total_duplicates > 0:
        dup_pct = duplicate_summary.duplicate_pct
        penalties += min(dup_pct * 0.5, 25.0)
        sev = IssueSeverity.WARNING if dup_pct > 5.0 else IssueSeverity.INFO
        issues.append(
            QualityIssue(
                title=f"{duplicate_summary.total_duplicates} Duplicate Row{'s' if duplicate_summary.total_duplicates > 1 else ''}",
                description=f"{dup_pct:.1f}% of observations are identical duplicates of earlier rows.",
                severity=sev,
                affected_columns=[],
            )
        )

    # 5. Evaluate missing values
    if missing_summary.total_missing_cells > 0:
        miss_pct = missing_summary.missing_cells_pct
        penalties += min(miss_pct * 0.5, 30.0)
        sev = IssueSeverity.WARNING if miss_pct > 10.0 else IssueSeverity.INFO
        issues.append(
            QualityIssue(
                title=f"{missing_summary.total_missing_cells} Missing Cell{'s' if missing_summary.total_missing_cells > 1 else ''} ({miss_pct:.1f}%)",
                description=f"{missing_summary.columns_with_missing_count} column(s) contain unrecorded/null entries.",
                severity=sev,
                affected_columns=[
                    row["Column"] for _, row in missing_summary.detail_table[missing_summary.detail_table["Missing Count"] > 0].iterrows()
                ],
            )
        )

    score = max(0.0, min(100.0, round(100.0 - penalties, 1)))

    if score >= 85.0 and len(issues) <= 1:
        status = "No major issues detected"
    elif score >= 65.0:
        status = "Some issues need attention"
    else:
        status = "Several data quality issues detected"

    return DataQualityReport(
        status=status,
        overall_health_score=score,
        issues=issues,
        missing_summary=missing_summary,
        duplicate_summary=duplicate_summary,
        variance_summary=variance_summary,
    )
