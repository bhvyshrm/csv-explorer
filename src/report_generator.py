"""Report generation engine for Analytix.

Generates:
1. Multi-tab Excel Analysis Workbook (.xlsx) using openpyxl
2. Consolidated Complete Analysis ZIP Archive (.zip) containing:
   - Executive Summary HTML Report (print/PDF-ready)
   - README explaining generated artifacts
   - Multi-tab Excel Workbook (.xlsx)
   - Machine-readable structured JSON report
   - Modular CSV exports (quality, statistics, correlations, outliers, columns)
"""

from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime, timezone
from typing import Any, Optional

import numpy as np
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd


def generate_analysis_workbook_xlsx(
    filename: str,
    overview: dict[str, Any],
    columns: list[dict[str, Any]],
    quality: dict[str, Any],
    numeric_stats: Optional[list[dict[str, Any]]] = None,
    correlation_matrix_df: Optional[pd.DataFrame] = None,
    outliers_map: Optional[dict[str, Any]] = None,
    dataset_format: str = "CSV",
    active_worksheet: Optional[str] = None,
) -> bytes:
    """Build a styled, professional multi-sheet Excel workbook summarizing dataset analytics."""
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="3B4252", end_color="3B4252", fill_type="solid")
    title_font = Font(name="Calibri", size=14, bold=True, color="2E3440")
    subtitle_font = Font(name="Calibri", size=10, italic=True, color="4C566A")
    thin_border = Border(
        left=Side(style="thin", color="D8DEE9"),
        right=Side(style="thin", color="D8DEE9"),
        top=Side(style="thin", color="D8DEE9"),
        bottom=Side(style="thin", color="D8DEE9"),
    )

    # 1. Sheet: Executive Summary
    ws_sum = wb.create_sheet(title="Executive_Summary")
    ws_sum.append(["Analytix — Dataset Executive Summary"])
    ws_sum.cell(row=1, column=1).font = title_font
    ws_sum.append([f"Generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"])
    ws_sum.cell(row=2, column=1).font = subtitle_font
    ws_sum.append([])

    summary_rows = [
        ("Dataset Name", filename),
        ("Dataset Format", dataset_format),
        ("Active Worksheet", active_worksheet or "N/A"),
        ("Total Rows", overview.get("total_rows", 0)),
        ("Total Columns", overview.get("total_columns", 0)),
        ("Total Cells", overview.get("total_cells", 0)),
        ("Memory Footprint", overview.get("memory_usage_formatted", "N/A")),
        ("Duplicate Rows", overview.get("total_duplicate_rows", 0)),
        ("Duplicate Rows (%)", f"{overview.get('duplicate_rows_pct', 0):.2f}%"),
        ("Total Missing Cells", overview.get("total_missing_cells", 0)),
        ("Missing Cells (%)", f"{overview.get('missing_cells_pct', 0):.2f}%"),
        ("Data Quality Health Score", f"{quality.get('overall_health_score', 100):.1f}/100"),
        ("Data Quality Status", quality.get("status", "N/A")),
    ]

    ws_sum.append(["Metric", "Value"])
    ws_sum.cell(row=4, column=1).font = header_font
    ws_sum.cell(row=4, column=1).fill = header_fill
    ws_sum.cell(row=4, column=2).font = header_font
    ws_sum.cell(row=4, column=2).fill = header_fill

    for metric, val in summary_rows:
        ws_sum.append([metric, val])

    for row in ws_sum.iter_rows(min_row=4, max_row=4 + len(summary_rows), min_col=1, max_col=2):
        for cell in row:
            cell.border = thin_border
    ws_sum.column_dimensions["A"].width = 28
    ws_sum.column_dimensions["B"].width = 36

    # 2. Sheet: Column Metadata
    if columns:
        ws_cols = wb.create_sheet(title="Column_Metadata")
        cols_df = pd.DataFrame(columns)
        for r in dataframe_to_rows(cols_df, index=False, header=True):
            ws_cols.append(r)
        for cell in ws_cols[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
        for col in ws_cols.columns:
            ws_cols.column_dimensions[col[0].column_letter].width = max(len(str(col[0].value or "")) + 6, 16)

    # 3. Sheet: Data Quality
    ws_qual = wb.create_sheet(title="Data_Quality")
    missing_detail = quality.get("missing_summary", {}).get("detail_table", [])
    if missing_detail:
        ws_qual.append(["Missing Values Audit"])
        ws_qual.cell(row=1, column=1).font = title_font
        ws_qual.append([])
        m_df = pd.DataFrame(missing_detail)
        for r in dataframe_to_rows(m_df, index=False, header=True):
            ws_qual.append(r)
        start_row = 3
        for cell in ws_qual[start_row]:
            cell.font = header_font
            cell.fill = header_fill
        for col in ws_qual.columns:
            ws_qual.column_dimensions[col[0].column_letter].width = 22

    # 4. Sheet: Numeric Statistics
    if numeric_stats:
        ws_stats = wb.create_sheet(title="Numeric_Statistics")
        stats_df = pd.DataFrame(numeric_stats)
        for r in dataframe_to_rows(stats_df, index=False, header=True):
            ws_stats.append(r)
        for cell in ws_stats[1]:
            cell.font = header_font
            cell.fill = header_fill
        for col in ws_stats.columns:
            ws_stats.column_dimensions[col[0].column_letter].width = 18

    # 5. Sheet: Correlation Matrix
    if correlation_matrix_df is not None and not correlation_matrix_df.empty:
        ws_corr = wb.create_sheet(title="Correlation_Matrix")
        for r in dataframe_to_rows(correlation_matrix_df, index=True, header=True):
            ws_corr.append(r)
        for cell in ws_corr[1]:
            cell.font = header_font
            cell.fill = header_fill
        for col in ws_corr.columns:
            ws_corr.column_dimensions[col[0].column_letter].width = 18

    # 6. Sheet: Outliers
    if outliers_map:
        ws_out = wb.create_sheet(title="Outlier_Analysis")
        outlier_rows = []
        for col_name, o in outliers_map.items():
            if isinstance(o, dict):
                outlier_rows.append(
                    {
                        "Column": col_name,
                        "Q1": o.get("q1"),
                        "Q3": o.get("q3"),
                        "IQR": o.get("iqr"),
                        "Lower Bound": o.get("lower_bound"),
                        "Upper Bound": o.get("upper_bound"),
                        "Flagged Count": o.get("flagged_count"),
                        "Flagged %": f"{o.get('flagged_pct', 0):.2f}%",
                    }
                )
        if outlier_rows:
            o_df = pd.DataFrame(outlier_rows)
            for r in dataframe_to_rows(o_df, index=False, header=True):
                ws_out.append(r)
            for cell in ws_out[1]:
                cell.font = header_font
                cell.fill = header_fill
            for col in ws_out.columns:
                ws_out.column_dimensions[col[0].column_letter].width = 18

    output_stream = io.BytesIO()
    wb.save(output_stream)
    return output_stream.getvalue()


def generate_executive_summary_html(
    filename: str,
    overview: dict[str, Any],
    quality: dict[str, Any],
    dataset_format: str = "CSV",
    active_worksheet: Optional[str] = None,
) -> str:
    """Generate a clean, print/PDF-ready HTML executive summary report."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    health_score = quality.get("overall_health_score", 100)
    health_color = "#10b981" if health_score >= 85 else "#f59e0b" if health_score >= 65 else "#ef4444"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Analytix Report — {filename}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.5; color: #1e293b; max-width: 900px; margin: 40px auto; padding: 0 24px; }}
  .header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 30px; }}
  .brand {{ font-size: 14px; text-transform: uppercase; letter-spacing: 0.1em; color: #6366f1; font-weight: 700; }}
  h1 {{ margin: 6px 0 4px 0; font-size: 26px; color: #0f172a; }}
  .meta {{ font-size: 13px; color: #64748b; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }}
  .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; }}
  .card-label {{ font-size: 12px; text-transform: uppercase; color: #64748b; font-weight: 600; margin-bottom: 6px; }}
  .card-value {{ font-size: 24px; font-weight: 700; color: #0f172a; }}
  .score {{ color: {health_color}; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 13px; }}
  th, td {{ border: 1px solid #e2e8f0; padding: 10px 14px; text-align: left; }}
  th {{ background: #f1f5f9; font-weight: 600; color: #334155; }}
  .footer {{ margin-top: 48px; padding-top: 20px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8; text-align: center; }}
</style>
</head>
<body>
  <div class="header">
    <div class="brand">Analytix • Data Exploration & Reporting</div>
    <h1>Executive Analysis Report</h1>
    <div class="meta">Target: <strong>{filename}</strong> | Format: {dataset_format} {f'({active_worksheet})' if active_worksheet else ''} | Generated: {now_str}</div>
  </div>

  <div class="grid">
    <div class="card">
      <div class="card-label">Total Rows</div>
      <div class="card-value">{overview.get('total_rows', 0):,}</div>
    </div>
    <div class="card">
      <div class="card-label">Total Columns</div>
      <div class="card-value">{overview.get('total_columns', 0):,}</div>
    </div>
    <div class="card">
      <div class="card-label">Data Quality Score</div>
      <div class="card-value score">{health_score:.1f}/100</div>
    </div>
    <div class="card">
      <div class="card-label">Duplicate Rows</div>
      <div class="card-value">{overview.get('total_duplicate_rows', 0):,} ({overview.get('duplicate_rows_pct', 0):.1f}%)</div>
    </div>
  </div>

  <h2>Dataset Dimensions & Classification</h2>
  <table>
    <tr><th>Metric</th><th>Observation</th></tr>
    <tr><td>Total Cells</td><td>{overview.get('total_cells', 0):,}</td></tr>
    <tr><td>Memory Footprint</td><td>{overview.get('memory_usage_formatted', 'N/A')}</td></tr>
    <tr><td>Numeric Columns</td><td>{len(overview.get('numeric_columns', []))} ({", ".join(overview.get('numeric_columns', [])[:8])})</td></tr>
    <tr><td>Categorical Columns</td><td>{len(overview.get('categorical_columns', []))} ({", ".join(overview.get('categorical_columns', [])[:8])})</td></tr>
    <tr><td>Missing Cells Count</td><td>{overview.get('total_missing_cells', 0):,} ({overview.get('missing_cells_pct', 0):.2f}%)</td></tr>
    <tr><td>Health Audit Status</td><td>{quality.get('status', 'N/A')}</td></tr>
  </table>

  <div class="footer">
    Analytix — Powerful data exploration and reporting, free to use.
  </div>
</body>
</html>
"""


def generate_complete_zip_report(
    filename: str,
    overview: dict[str, Any],
    columns: list[dict[str, Any]],
    quality: dict[str, Any],
    numeric_stats: Optional[list[dict[str, Any]]] = None,
    correlation_matrix_df: Optional[pd.DataFrame] = None,
    outliers_map: Optional[dict[str, Any]] = None,
    preview_rows: Optional[list[dict[str, Any]]] = None,
    dataset_format: str = "CSV",
    active_worksheet: Optional[str] = None,
) -> bytes:
    """Package all analysis artifacts into a single consolidated ZIP archive."""
    clean_prefix = (
        filename.replace(".csv", "")
        .replace(".xlsx", "")
        .replace(".xls", "")
        .replace(".json", "")
        .replace(".parquet", "")
        .replace(".tsv", "")
        .replace(".txt", "")
        .replace(".log", "")
        .replace(".xml", "")
    )
    if active_worksheet:
        clean_prefix += f"_{active_worksheet}"

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. README.txt
        readme_content = f"""==================================================
ANALYTIX COMPLETE ANALYSIS ARCHIVE
==================================================
Target Dataset: {filename}
Format: {dataset_format}
Active Sheet: {active_worksheet or "N/A"}
Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
Product: Analytix (https://github.com/bhvyshrm/csv-explorer)

INCLUDED ARTIFACTS:
1. summary_report.html
   - Standalone, print/PDF-ready executive analysis summary.
2. {clean_prefix}_analysis_workbook.xlsx
   - Comprehensive multi-tab spreadsheet containing Overview, Column Metadata,
     Data Quality, Descriptive Statistics, Correlation Matrix, and Outliers.
3. {clean_prefix}_eda_report.json
   - Machine-readable structured JSON report containing dimensions,
     quality heuristics, and statistical metrics.
4. {clean_prefix}_column_metadata.csv
   - Column names, inferred types, missing counts, unique values, and memory.
5. {clean_prefix}_missing_values.csv
   - Detailed missing value audit table by column.
6. {clean_prefix}_numeric_statistics.csv
   - Standard descriptive statistics (mean, median, std, quartiles, IQR, min, max).
7. {clean_prefix}_correlation_matrix.csv
   - Numeric correlation matrix (if numeric columns >= 2).
8. {clean_prefix}_outliers_report.csv
   - IQR-detected outliers and distribution bounds.
9. {clean_prefix}_sample_preview.csv
   - Sample row preview from the dataset.

Analytix — Explore data. Discover insights. Powerful data exploration and reporting, free to use.
"""
        zf.writestr("README.txt", readme_content)

        # 2. summary_report.html
        html_report = generate_executive_summary_html(
            filename=filename,
            overview=overview,
            quality=quality,
            dataset_format=dataset_format,
            active_worksheet=active_worksheet,
        )
        zf.writestr(f"{clean_prefix}_summary_report.html", html_report)

        # 3. Multi-sheet Excel Workbook (.xlsx)
        xlsx_bytes = generate_analysis_workbook_xlsx(
            filename=filename,
            overview=overview,
            columns=columns,
            quality=quality,
            numeric_stats=numeric_stats,
            correlation_matrix_df=correlation_matrix_df,
            outliers_map=outliers_map,
            dataset_format=dataset_format,
            active_worksheet=active_worksheet,
        )
        zf.writestr(f"{clean_prefix}_analysis_workbook.xlsx", xlsx_bytes)

        # 4. JSON Report
        json_report_data = {
            "application": "Analytix",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "dataset_name": filename,
            "dataset_format": dataset_format,
            "active_worksheet": active_worksheet,
            "overview": overview,
            "columns": columns,
            "quality": quality,
            "numeric_statistics": numeric_stats,
            "outliers": outliers_map,
        }
        zf.writestr(
            f"{clean_prefix}_eda_report.json",
            json.dumps(json_report_data, indent=2, default=str),
        )

        # 5. Column metadata CSV
        if columns:
            cols_df = pd.DataFrame(columns)
            zf.writestr(f"{clean_prefix}_column_metadata.csv", cols_df.to_csv(index=False))

        # 6. Missing values CSV
        missing_detail = quality.get("missing_summary", {}).get("detail_table", [])
        if missing_detail:
            m_df = pd.DataFrame(missing_detail)
            zf.writestr(f"{clean_prefix}_missing_values.csv", m_df.to_csv(index=False))

        # 7. Numeric stats CSV
        if numeric_stats:
            stats_df = pd.DataFrame(numeric_stats)
            zf.writestr(f"{clean_prefix}_numeric_statistics.csv", stats_df.to_csv(index=False))

        # 8. Correlation matrix CSV
        if correlation_matrix_df is not None and not correlation_matrix_df.empty:
            zf.writestr(
                f"{clean_prefix}_correlation_matrix.csv",
                correlation_matrix_df.to_csv(index=True),
            )

        # 9. Outliers CSV
        if outliers_map:
            outlier_rows = []
            for col_name, o in outliers_map.items():
                if isinstance(o, dict):
                    outlier_rows.append(
                        {
                            "Column": col_name,
                            "Q1": o.get("q1"),
                            "Q3": o.get("q3"),
                            "IQR": o.get("iqr"),
                            "Lower Bound": o.get("lower_bound"),
                            "Upper Bound": o.get("upper_bound"),
                            "Flagged Outliers Count": o.get("flagged_count"),
                            "Flagged Outliers Pct": f"{o.get('flagged_pct', 0):.2f}%",
                        }
                    )
            if outlier_rows:
                o_df = pd.DataFrame(outlier_rows)
                zf.writestr(f"{clean_prefix}_outliers_report.csv", o_df.to_csv(index=False))

        # 10. Sample preview CSV
        if preview_rows:
            p_df = pd.DataFrame(preview_rows)
            zf.writestr(f"{clean_prefix}_sample_preview.csv", p_df.to_csv(index=False))

    return zip_buffer.getvalue()
