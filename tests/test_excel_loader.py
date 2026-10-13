"""Unit tests for Excel loader module (src/excel_loader.py)."""

import io
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

from src.excel_loader import (
    inspect_excel_workbook,
    load_excel_sheet,
    ExcelCorruptedError,
    ExcelUnsupportedFormatError,
    ExcelSheetNotFoundError,
    ExcelEmptySheetError,
)
from src.data_overview import get_dataset_overview, get_column_metadata
from src.data_quality import generate_data_quality_report
from src.statistics import get_numeric_statistics
from src.outliers import detect_outliers_iqr
from src.export import generate_json_report


SAMPLE_EXCEL_PATH = Path("sample_data/sample_analytix_multisheet.xlsx")


def test_inspect_sample_excel_workbook():
    assert SAMPLE_EXCEL_PATH.exists()
    meta = inspect_excel_workbook(SAMPLE_EXCEL_PATH)
    assert meta.total_sheets == 3
    assert "Orders_Data" in meta.sheet_names
    assert "Customer_Demographics" in meta.sheet_names
    assert "Empty_Template" in meta.sheet_names
    assert meta.file_format == ".xlsx"


def test_load_orders_sheet_valid():
    res = load_excel_sheet(SAMPLE_EXCEL_PATH, sheet_name="Orders_Data")
    df = res.df
    assert len(df) == 101
    assert "Order_ID" in df.columns
    assert "Sales" in df.columns
    assert "Profit" in df.columns
    assert res.metadata.filename == "sample_analytix_multisheet.xlsx"
    assert df.attrs["active_worksheet"] == "Orders_Data"
    assert "Excel" in df.attrs["source_format"]


def test_selecting_different_worksheets():
    res1 = load_excel_sheet(SAMPLE_EXCEL_PATH, sheet_name="Orders_Data")
    res2 = load_excel_sheet(SAMPLE_EXCEL_PATH, sheet_name="Customer_Demographics")

    assert len(res1.df) == 101
    assert len(res2.df) == 50
    assert "Sales" in res1.df.columns
    assert "Sales" not in res2.df.columns
    assert "Income" in res2.df.columns


def test_empty_sheet_handling():
    res = load_excel_sheet(SAMPLE_EXCEL_PATH, sheet_name="Empty_Template")
    # Headers present, but 0 data rows
    assert len(res.df) == 0
    assert list(res.df.columns) == ["Template_Field_A", "Template_Field_B", "Template_Field_C"]
    assert res.metadata.has_headers_only is True
    assert any("headers but zero data rows" in w for w in res.metadata.warnings)


def test_excel_missing_values_preserved():
    res = load_excel_sheet(SAMPLE_EXCEL_PATH, sheet_name="Orders_Data")
    df = res.df
    # Injected nulls in Profit
    assert df["Profit"].isna().sum() > 0


def test_excel_duplicate_rows_detected():
    res = load_excel_sheet(SAMPLE_EXCEL_PATH, sheet_name="Orders_Data")
    df = res.df
    report = generate_data_quality_report(df)
    assert report.duplicate_summary.total_duplicates >= 1


def test_excel_constant_columns_detected():
    res = load_excel_sheet(SAMPLE_EXCEL_PATH, sheet_name="Customer_Demographics")
    df = res.df
    report = generate_data_quality_report(df)
    assert "Country" in report.variance_summary.constant_columns
    assert report.variance_summary.constant_columns["Country"] == "United States"


def test_excel_date_columns_parsed():
    res = load_excel_sheet(SAMPLE_EXCEL_PATH, sheet_name="Orders_Data")
    df = res.df
    assert pd.api.types.is_datetime64_any_dtype(df["Order_Date"])


def test_corrupted_excel_file_raises_error():
    bad_bytes = io.BytesIO(b"This is not a valid zip or excel workbook at all.")
    bad_bytes.name = "corrupted.xlsx"
    with pytest.raises(ExcelCorruptedError):
        load_excel_sheet(bad_bytes)


def test_unsupported_extension_raises_error():
    fake_txt = io.BytesIO(b"some,data\n1,2\n")
    fake_txt.name = "document.pdf"
    with pytest.raises(ExcelUnsupportedFormatError):
        load_excel_sheet(fake_txt)


def test_nonexistent_sheet_raises_error():
    with pytest.raises(ExcelSheetNotFoundError):
        load_excel_sheet(SAMPLE_EXCEL_PATH, sheet_name="Non_Existent_Sheet_123")


def test_excel_integration_with_eda_pipeline():
    res = load_excel_sheet(SAMPLE_EXCEL_PATH, sheet_name="Orders_Data")
    df = res.df

    # Overview
    overview = get_dataset_overview(df)
    assert overview.total_rows == 101
    assert "Sales" in overview.numeric_columns
    assert "Category" in overview.categorical_columns
    assert "Order_Date" in overview.datetime_columns

    # Column metadata
    meta_df = get_column_metadata(df)
    assert len(meta_df) == 8

    # Statistics
    stats_df = get_numeric_statistics(df)
    assert "Sales" in stats_df.columns

    # Outliers
    outliers = detect_outliers_iqr(df, "Sales")
    assert outliers.flagged_count >= 1
    assert outliers.upper_outliers_count >= 1

    # Export report with active worksheet metadata
    json_str = generate_json_report(
        filename="sample_analytix_multisheet.xlsx",
        overview_dict={"rows": overview.total_rows, "cols": overview.total_columns},
        column_metadata_df=meta_df,
        dataset_format="Excel (.xlsx)",
        active_worksheet="Orders_Data",
    )
    import json
    parsed = json.loads(json_str)
    assert parsed["application"] == "Analytix"
    assert parsed["dataset_format"] == "Excel (.xlsx)"
    assert parsed["active_worksheet"] == "Orders_Data"
