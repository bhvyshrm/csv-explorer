"""Unit tests for src/data_overview.py."""

import pandas as pd
import numpy as np
from src.data_overview import (
    get_dataset_overview,
    get_column_metadata,
    classify_columns,
    format_bytes,
    get_column_sample_values,
)


def test_format_bytes():
    assert format_bytes(500) == "500 B"
    assert format_bytes(2048) == "2.00 KB"
    assert format_bytes(1048576) == "1.00 MB"


def test_classify_columns():
    df = pd.DataFrame({
        "num_int": [1, 2, 3],
        "num_float": [1.1, 2.2, 3.3],
        "cat_str": ["a", "b", "c"],
        "bool_flag": [True, False, True],
        "date_col": pd.date_range("2024-01-01", periods=3),
    })

    classified = classify_columns(df)
    assert "num_int" in classified["numeric"]
    assert "num_float" in classified["numeric"]
    assert "bool_flag" in classified["boolean"]
    # Boolean should NOT be in numeric!
    assert "bool_flag" not in classified["numeric"]
    assert "cat_str" in classified["categorical"]
    assert "date_col" in classified["datetime"]


def test_get_dataset_overview():
    df = pd.DataFrame({
        "id": [1, 2, 3, 3],
        "val": [10.0, np.nan, 30.0, 30.0],
        "name": ["A", "B", "C", "C"],
    })
    overview = get_dataset_overview(df)
    assert overview.total_rows == 4
    assert overview.total_columns == 3
    assert overview.total_cells == 12
    assert overview.total_missing_cells == 1
    assert overview.missing_cells_pct == round((1 / 12) * 100, 2)
    # One duplicated row (row index 3 is duplicate of row 2)
    assert overview.total_duplicate_rows == 1
    assert overview.duplicate_rows_pct == 25.0
    assert "id" in overview.numeric_columns
    assert "val" in overview.numeric_columns
    assert "name" in overview.categorical_columns


def test_get_column_metadata():
    df = pd.DataFrame({
        "age": [25, 30, np.nan],
        "city": ["NYC", "LA", "NYC"],
    })
    meta = get_column_metadata(df)
    assert len(meta) == 2
    assert list(meta["Column Name"]) == ["age", "city"]

    age_row = meta[meta["Column Name"] == "age"].iloc[0]
    assert age_row["Missing Count"] == 1
    assert age_row["Non-Null Count"] == 2
    assert age_row["Missing %"] == 33.33
    assert age_row["Unique Values"] == 2

    city_row = meta[meta["Column Name"] == "city"].iloc[0]
    assert city_row["Missing Count"] == 0
    assert city_row["Unique Values"] == 2


def test_get_column_sample_values():
    df = pd.DataFrame({"x": [10, 20, np.nan, 40]})
    samples = get_column_sample_values(df, "x", n_samples=2)
    assert samples == [10.0, 20.0]
    assert get_column_sample_values(df, "non_existent") == []
