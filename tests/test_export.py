"""Unit tests for src/export.py."""

import json
import numpy as np
import pandas as pd
from src.export import export_dataframe_to_csv, generate_json_report, _sanitize_for_json


def test_export_dataframe_to_csv():
    df = pd.DataFrame({"col_a": [1, 2], "col_b": ["apple", "banana"]})
    csv_bytes = export_dataframe_to_csv(df)
    assert isinstance(csv_bytes, bytes)
    content = csv_bytes.decode("utf-8")
    assert "col_a,col_b" in content
    assert "1,apple" in content
    assert "2,banana" in content


def test_sanitize_for_json_handles_nan_and_numpy():
    raw_data = {
        "float_val": np.float64(3.14),
        "int_val": np.int32(42),
        "nan_val": np.nan,
        "inf_val": np.inf,
        "bool_val": np.bool_(True),
        "nested": [np.nan, 100],
    }
    cleaned = _sanitize_for_json(raw_data)
    assert cleaned["float_val"] == 3.14
    assert cleaned["int_val"] == 42
    assert cleaned["nan_val"] is None
    assert cleaned["inf_val"] is None
    assert cleaned["bool_val"] is True
    assert cleaned["nested"] == [None, 100]

    # Verify standard json serialization succeeds without error
    json_str = json.dumps(cleaned)
    assert isinstance(json_str, str)


def test_generate_json_report():
    overview = {
        "rows": 100,
        "columns": 5,
        "memory": "15 KB",
    }
    cols_df = pd.DataFrame({
        "Column Name": ["age", "income"],
        "Missing %": [0.0, 5.0],
    })
    quality = {
        "status": "No major issues detected",
        "score": 98.0,
    }

    report_str = generate_json_report(
        filename="test_dataset.csv",
        overview_dict=overview,
        column_metadata_df=cols_df,
        quality_summary_dict=quality,
    )

    parsed = json.loads(report_str)
    assert parsed["application"] == "Analytix"
    assert parsed["dataset_name"] == "test_dataset.csv"
    assert parsed["overview"]["rows"] == 100
    assert len(parsed["columns"]) == 2
    assert parsed["data_quality"]["status"] == "No major issues detected"
