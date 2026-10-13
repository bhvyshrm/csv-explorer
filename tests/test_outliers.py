"""Unit tests for src/outliers.py."""

import numpy as np
import pandas as pd
from src.outliers import detect_outliers_iqr


def test_standard_iqr_outliers_detection():
    # Regular values: 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20
    # Add clear lower outlier (-50) and upper outlier (150)
    vals = [-50.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 150.0]
    df = pd.DataFrame({"metric": vals})
    orig_copy = df.copy()

    res = detect_outliers_iqr(df, "metric", multiplier=1.5)

    assert res.flagged_count == 2
    assert res.lower_outliers_count == 1
    assert res.upper_outliers_count == 1
    assert res.valid_observations_count == 13
    assert -50.0 in res.flagged_df["metric"].values
    assert 150.0 in res.flagged_df["metric"].values
    assert 15.0 not in res.flagged_df["metric"].values

    # Check non-destructive rule: original dataframe unchanged
    pd.testing.assert_frame_equal(df, orig_copy)


def test_iqr_handles_missing_values():
    # Values with NaN entries
    vals = [np.nan, 10.0, 12.0, 11.0, 14.0, 13.0, 12.0, 11.0, 500.0, np.nan]
    df = pd.DataFrame({"score": vals})

    res = detect_outliers_iqr(df, "score")
    assert res.valid_observations_count == 8
    assert res.upper_outliers_count == 1
    assert 500.0 in res.flagged_df["score"].values
    # NaNs must NOT be flagged as outliers
    assert res.flagged_df["score"].isna().sum() == 0


def test_iqr_insufficient_observations():
    df = pd.DataFrame({"val": [1.0, 2.0, 3.0]})
    res = detect_outliers_iqr(df, "val")
    assert res.valid_observations_count == 3
    assert res.flagged_count == 0
    assert "Insufficient" in res.status_message


def test_iqr_constant_column():
    df = pd.DataFrame({"val": [5.0] * 10})
    res = detect_outliers_iqr(df, "val")
    assert res.valid_observations_count == 10
    assert res.iqr == 0.0
    assert res.flagged_count == 0
