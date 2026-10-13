"""Unit tests for src/statistics.py."""

import numpy as np
import pandas as pd
from src.statistics import (
    get_numeric_columns,
    compute_column_numeric_stats,
    get_numeric_statistics,
    get_categorical_statistics,
)


def test_get_numeric_columns_excludes_boolean():
    df = pd.DataFrame({
        "num_a": [1, 2, 3],
        "num_b": [4.0, 5.5, 6.2],
        "is_active": [True, False, True],
        "category": ["A", "B", "C"],
    })
    numeric_cols = get_numeric_columns(df)
    assert "num_a" in numeric_cols
    assert "num_b" in numeric_cols
    assert "is_active" not in numeric_cols
    assert "category" not in numeric_cols


def test_numeric_stats_standard_values():
    # Values: 10, 20, 30, 40, 50
    series = pd.Series([10, 20, 30, 40, 50], dtype=float)
    stats = compute_column_numeric_stats(series, "test_col")
    assert stats.count == 5
    assert stats.missing == 0
    assert stats.mean == 30.0
    assert stats.median == 30.0
    assert stats.min == 10.0
    assert stats.max == 50.0
    assert stats.q1 == 20.0
    assert stats.q3 == 40.0
    assert stats.iqr == 20.0
    # Sample std of [10, 20, 30, 40, 50] with ddof=1 is sqrt(250) ~ 15.8114
    assert round(stats.std, 2) == 15.81
    assert stats.skewness == 0.0


def test_numeric_stats_edge_cases():
    # 1. Single observation
    single = pd.Series([42.0])
    s_stats = compute_column_numeric_stats(single, "single")
    assert s_stats.count == 1
    assert s_stats.mean == 42.0
    # std and variance must be None, NOT 0.0
    assert s_stats.std is None
    assert s_stats.variance is None
    assert s_stats.skewness is None

    # 2. All missing
    all_nan = pd.Series([np.nan, np.nan])
    nan_stats = compute_column_numeric_stats(all_nan, "all_nan")
    assert nan_stats.count == 0
    assert nan_stats.mean is None
    assert nan_stats.std is None

    # 3. Constant column
    const = pd.Series([7.0, 7.0, 7.0, 7.0])
    c_stats = compute_column_numeric_stats(const, "const")
    assert c_stats.count == 4
    assert c_stats.mean == 7.0
    assert c_stats.std == 0.0
    assert c_stats.iqr == 0.0


def test_get_numeric_statistics_dataframe():
    df = pd.DataFrame({
        "x": [1.0, 2.0, 3.0, 4.0],
        "y": [10.0, 20.0, np.nan, 40.0],
    })
    table = get_numeric_statistics(df)
    assert "Metric" in table.columns
    assert "x" in table.columns
    assert "y" in table.columns
    assert len(table) > 10


def test_categorical_statistics():
    df = pd.DataFrame({
        "color": ["Red", "Blue", "Red", "Green", "Red", "Blue", None],
    })
    cat_stats = get_categorical_statistics(df, "color", top_n=2)
    assert cat_stats.column == "color"
    assert cat_stats.total_observations == 7
    assert cat_stats.missing_observations == 1
    assert cat_stats.unique_count == 3
    assert cat_stats.most_frequent_value == "Red"
    assert cat_stats.most_frequent_count == 3
    # Top 2 requested, so 1 distinct value (Green) was omitted from the top 2 table
    assert cat_stats.total_distinct_omitted == 1
    assert len(cat_stats.frequency_table) == 2
    assert cat_stats.frequency_table.iloc[0]["Value"] == "Red"
    assert cat_stats.frequency_table.iloc[0]["Count"] == 3
