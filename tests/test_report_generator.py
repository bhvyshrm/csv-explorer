"""Unit tests for Analytix report generator (XLSX workbook & ZIP archive)."""

import io
import zipfile
import openpyxl
import pandas as pd
import pytest

from src.report_generator import (
    generate_analysis_workbook_xlsx,
    generate_complete_zip_report,
    generate_executive_summary_html,
)


@pytest.fixture
def mock_dataset_payload():
    return {
        "filename": "test_sales.csv",
        "dataset_format": "CSV",
        "overview": {
            "total_rows": 50,
            "total_columns": 4,
            "total_cells": 200,
            "memory_usage_formatted": "12.5 KB",
            "total_duplicate_rows": 0,
            "duplicate_rows_pct": 0.0,
            "total_missing_cells": 2,
            "missing_cells_pct": 1.0,
            "numeric_columns": ["Sales", "Profit"],
            "categorical_columns": ["Region", "Segment"],
        },
        "columns": [
            {
                "Column Name": "Sales",
                "Inferred Type": "Numeric",
                "Python dtype": "float64",
                "Missing Count": 0,
                "Missing %": 0.0,
                "Unique Values": 45,
                "Memory (Bytes)": 400,
            },
            {
                "Column Name": "Region",
                "Inferred Type": "Categorical",
                "Python dtype": "object",
                "Missing Count": 0,
                "Missing %": 0.0,
                "Unique Values": 4,
                "Memory (Bytes)": 800,
            },
        ],
        "quality": {
            "status": "Good",
            "overall_health_score": 95.0,
            "missing_summary": {
                "detail_table": [
                    {
                        "Column": "Profit",
                        "Missing Count": 2,
                        "Missing %": 4.0,
                        "Non-Missing Count": 48,
                    }
                ]
            },
        },
        "numeric_stats": [
            {"Statistic": "mean", "Sales": 250.5, "Profit": 45.2},
            {"Statistic": "std", "Sales": 120.3, "Profit": 25.1},
        ],
        "correlation_df": pd.DataFrame([[1.0, 0.78], [0.78, 1.0]], index=["Sales", "Profit"], columns=["Sales", "Profit"]),
        "outliers_map": {
            "Sales": {
                "q1": 150.0,
                "q3": 350.0,
                "iqr": 200.0,
                "lower_bound": -150.0,
                "upper_bound": 650.0,
                "flagged_count": 2,
                "flagged_pct": 4.0,
            }
        },
        "preview_rows": [{"Sales": 100, "Profit": 20, "Region": "West", "Segment": "Consumer"}],
    }


def test_generate_analysis_workbook_xlsx(mock_dataset_payload):
    """Verify Excel analysis workbook contains expected sheets and headers."""
    xlsx_bytes = generate_analysis_workbook_xlsx(
        filename=mock_dataset_payload["filename"],
        overview=mock_dataset_payload["overview"],
        columns=mock_dataset_payload["columns"],
        quality=mock_dataset_payload["quality"],
        numeric_stats=mock_dataset_payload["numeric_stats"],
        correlation_matrix_df=mock_dataset_payload["correlation_df"],
        outliers_map=mock_dataset_payload["outliers_map"],
    )
    assert len(xlsx_bytes) > 0

    wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))
    sheet_names = wb.sheetnames
    assert "Executive_Summary" in sheet_names
    assert "Column_Metadata" in sheet_names
    assert "Data_Quality" in sheet_names
    assert "Numeric_Statistics" in sheet_names
    assert "Correlation_Matrix" in sheet_names
    assert "Outlier_Analysis" in sheet_names


def test_generate_executive_summary_html(mock_dataset_payload):
    """Verify HTML executive report contains key metrics and branding."""
    html_content = generate_executive_summary_html(
        filename=mock_dataset_payload["filename"],
        overview=mock_dataset_payload["overview"],
        quality=mock_dataset_payload["quality"],
    )
    assert "Executive Analysis Report" in html_content
    assert "test_sales.csv" in html_content
    assert "Analytix" in html_content
    assert "95.0/100" in html_content


def test_generate_complete_zip_report(mock_dataset_payload):
    """Verify complete ZIP archive packages all reports and README correctly."""
    zip_bytes = generate_complete_zip_report(
        filename=mock_dataset_payload["filename"],
        overview=mock_dataset_payload["overview"],
        columns=mock_dataset_payload["columns"],
        quality=mock_dataset_payload["quality"],
        numeric_stats=mock_dataset_payload["numeric_stats"],
        correlation_matrix_df=mock_dataset_payload["correlation_df"],
        outliers_map=mock_dataset_payload["outliers_map"],
        preview_rows=mock_dataset_payload["preview_rows"],
    )
    assert len(zip_bytes) > 0

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        namelist = zf.namelist()
        assert "README.txt" in namelist
        assert any("summary_report.html" in n for n in namelist)
        assert any("analysis_workbook.xlsx" in n for n in namelist)
        assert any("eda_report.json" in n for n in namelist)
        assert any("column_metadata.csv" in n for n in namelist)
        assert any("missing_values.csv" in n for n in namelist)
        assert any("numeric_statistics.csv" in n for n in namelist)
        assert any("correlation_matrix.csv" in n for n in namelist)
        assert any("outliers_report.csv" in n for n in namelist)
        assert any("sample_preview.csv" in n for n in namelist)

        # Check README content
        readme_text = zf.read("README.txt").decode("utf-8")
        assert "ANALYTIX COMPLETE ANALYSIS ARCHIVE" in readme_text
        assert "test_sales.csv" in readme_text
