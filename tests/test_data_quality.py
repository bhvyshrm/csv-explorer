"""Unit tests for src/data_quality.py."""

import numpy as np
import pandas as pd
from src.data_quality import (
    analyze_missing_values,
    analyze_duplicates,
    analyze_column_variance,
    generate_data_quality_report,
)


def test_missing_values_analysis():
    df = pd.DataFrame({
        "col_a": [1, 2, np.nan, 4],
        "col_b": [np.nan, np.nan, "x", "y"],
        "col_c": [10, 20, 30, 40],
    })

    res = analyze_missing_values(df)
    assert res.total_missing_cells == 3
    assert res.columns_with_missing_count == 2
    assert res.missing_cells_pct == round((3 / 12) * 100.0, 2)

    table = res.detail_table
    assert len(table) == 3
    row_b = table[table["Column"] == "col_b"].iloc[0]
    assert row_b["Missing Count"] == 2
    assert row_b["Missing %"] == 50.0
    assert row_b["Non-Missing Count"] == 2


def test_duplicates_analysis():
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Alice", "Alice"],
        "age": [25, 30, 25, 25],
    })

    res = analyze_duplicates(df)
    # Rows at index 2 and 3 are duplicates of row 0
    assert res.total_duplicates == 2
    assert res.duplicate_pct == 50.0
    assert res.rows_remaining_after_dedup == 2
    assert len(res.duplicate_rows_preview) > 0


def test_constant_and_empty_columns():
    df = pd.DataFrame({
        "all_null": [np.nan, np.nan, np.nan, np.nan],
        "nearly_empty": [np.nan, np.nan, np.nan, 42.0],  # 75% missing
        "constant": ["ACTIVE", "ACTIVE", "ACTIVE", "ACTIVE"],
        "normal": [1, 2, 3, 4],
    })

    res = analyze_column_variance(df, nearly_empty_threshold_pct=70.0)
    assert "all_null" in res.entirely_empty_columns
    assert "nearly_empty" in res.nearly_empty_columns
    assert "constant" in res.constant_columns
    assert res.constant_columns["constant"] == "ACTIVE"
    # Constant column should not include all_null!
    assert "all_null" not in res.constant_columns
    assert "normal" not in res.constant_columns


def test_quality_summary_clean_dataset():
    df = pd.DataFrame({
        "a": [1, 2, 3, 4, 5],
        "b": ["x", "y", "z", "w", "v"],
    })
    report = generate_data_quality_report(df)
    assert report.status == "No major issues detected"
    assert report.overall_health_score == 100.0
    assert len(report.issues) == 0


def test_quality_summary_degraded_dataset():
    df = pd.DataFrame({
        "null_col": [np.nan] * 10,
        "constant_col": [1] * 10,
        "dup_col": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    })
    report = generate_data_quality_report(df)
    assert report.status in ["Some issues need attention", "Several data quality issues detected"]
    assert len(report.issues) >= 2
    assert report.overall_health_score < 85.0
