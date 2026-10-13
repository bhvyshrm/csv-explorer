"""End-to-end integration test validating the full EDA pipeline with sample data."""

import json
from pathlib import Path
import pytest

from src.data_loader import load_csv_detailed
from src.data_overview import get_dataset_overview, get_column_metadata
from src.data_quality import generate_data_quality_report
from src.statistics import get_numeric_statistics, get_categorical_statistics
from src.outliers import detect_outliers_iqr
from src.visualizations import (
    create_histogram,
    create_box_plot,
    create_categorical_bar_chart,
    create_correlation_heatmap,
)
from src.export import export_dataframe_to_csv, generate_json_report


def test_full_eda_pipeline_on_sample_superstore():
    sample_file = Path("sample_data/sample_superstore_eda.csv")
    assert sample_file.exists()

    # Step 1: Load CSV
    res = load_csv_detailed(sample_file)
    df = res.df
    assert len(df) == 122
    assert len(df.columns) == 16
    assert res.metadata.file_size_bytes > 0

    # Step 2: Overview
    overview = get_dataset_overview(df)
    assert overview.total_rows == 122
    assert overview.total_columns == 16
    assert "Sales" in overview.numeric_columns
    assert "Profit" in overview.numeric_columns
    assert "Category" in overview.categorical_columns
    assert "Store_Status" in overview.categorical_columns or "Store_Status" in df.columns
    assert overview.total_duplicate_rows == 2  # exactly 2 duplicates added

    # Step 3: Column Metadata
    meta_df = get_column_metadata(df)
    assert len(meta_df) == 16
    assert "Column Name" in meta_df.columns
    assert "Missing Count" in meta_df.columns

    # Step 4: Data Quality Audit
    quality_report = generate_data_quality_report(df)
    assert quality_report.duplicate_summary.total_duplicates == 2
    assert "Store_Status" in quality_report.variance_summary.constant_columns
    assert quality_report.variance_summary.constant_columns["Store_Status"] == "Active"
    assert quality_report.missing_summary.total_missing_cells > 0
    assert len(quality_report.issues) >= 3

    # Step 5: Statistics
    num_stats = get_numeric_statistics(df)
    assert not num_stats.empty
    assert "Sales" in num_stats.columns
    assert "Profit" in num_stats.columns

    cat_stats = get_categorical_statistics(df, "Category", top_n=5)
    assert cat_stats.unique_count == 3
    assert cat_stats.most_frequent_value in ["Technology", "Furniture", "Office Supplies"]

    # Step 6: Outliers
    sales_outliers = detect_outliers_iqr(df, "Sales", multiplier=1.5)
    assert sales_outliers.flagged_count >= 2
    assert sales_outliers.upper_outliers_count >= 2
    assert len(sales_outliers.flagged_df) == sales_outliers.flagged_count

    # Step 7: Visualizations
    fig_hist = create_histogram(df, "Sales")
    fig_box = create_box_plot(df, "Profit")
    fig_bar = create_categorical_bar_chart(df, "Region")
    fig_corr = create_correlation_heatmap(df, columns=["Sales", "Quantity", "Discount", "Profit"])

    assert fig_hist.data[0].type == "histogram"
    assert fig_box.data[0].type == "box"
    assert fig_bar.data[0].type == "bar"
    assert fig_corr.data[0].type == "heatmap"

    # Step 8: Export
    csv_bytes = export_dataframe_to_csv(meta_df)
    assert len(csv_bytes) > 0

    json_str = generate_json_report(
        filename="sample_superstore_eda.csv",
        overview_dict={"rows": overview.total_rows, "cols": overview.total_columns},
        column_metadata_df=meta_df,
        quality_summary_dict={"status": quality_report.status},
        numeric_stats_df=num_stats,
    )
    parsed = json.loads(json_str)
    assert parsed["application"] == "CSV Explorer"
    assert parsed["dataset_name"] == "sample_superstore_eda.csv"
