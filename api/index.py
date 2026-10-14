"""Analytix 2.0 - Vercel-Compatible FastAPI Serverless Entrypoint.

Bridges the native data science engine in src/ (pandas, numpy, openpyxl, plotly)
with Vercel's Python serverless function runtime (@vercel/python).
"""

from __future__ import annotations

import io
import json
import math
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.data_loader import (
    CSVEmptyError,
    CSVEncodingError,
    CSVParsingError,
    CSVSizeLimitExceededError,
    load_csv_detailed,
)
from src.data_overview import (
    classify_columns,
    get_column_metadata,
    get_dataset_overview,
)
from src.data_quality import (
    DataQualityReport,
    generate_data_quality_report,
)
from src.excel_loader import (
    ExcelCorruptedError,
    ExcelEmptySheetError,
    ExcelEmptyWorkbookError,
    ExcelSheetNotFoundError,
    ExcelUnsupportedFormatError,
    WorkbookMetadata,
    inspect_excel_workbook,
    load_excel_sheet,
)
from src.export import (
    export_dataframe_to_csv,
    generate_json_report,
)
from src.outliers import detect_outliers_iqr
from src.statistics import (
    get_categorical_statistics,
    get_numeric_statistics,
)
from src.visualizations import (
    create_box_plot,
    create_categorical_bar_chart,
    create_correlation_heatmap,
    create_histogram,
    create_missing_values_bar_chart,
)

# Vercel Serverless hard limit is 4.5 MB.
MAX_SERVERLESS_BYTES = int(4.5 * 1024 * 1024)

SAMPLE_CSV_PATH = Path("sample_data/sample_superstore_eda.csv")
SAMPLE_EXCEL_PATH = Path("sample_data/sample_analytix_multisheet.xlsx")

app = FastAPI(
    title="Analytix API",
    description="Multi-Format Data Exploration and Statistical Engine",
    version="2.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# Enable CORS for local and cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def sanitize_for_json(val: Any) -> Any:
    """Recursively convert NumPy/Pandas objects, non-finite floats, and dates to JSON-safe primitives."""
    if val is None:
        return None
    if isinstance(val, (float, np.floating)):
        if math.isnan(val) or math.isinf(val):
            return None
        return float(val)
    if isinstance(val, (int, np.integer)):
        return int(val)
    if isinstance(val, (bool, np.bool_)):
        return bool(val)
    if isinstance(val, pd.Timestamp):
        return val.isoformat()
    if isinstance(val, dict):
        return {str(k): sanitize_for_json(v) for k, v in val.items()}
    if isinstance(val, (list, tuple, set)):
        return [sanitize_for_json(v) for v in val]
    if isinstance(val, pd.DataFrame):
        return sanitize_for_json(val.to_dict(orient="records"))
    return str(val) if not isinstance(val, (str, int, float, bool)) else val


def _create_named_buffer(content: bytes, filename: str) -> io.BytesIO:
    """Create a BytesIO stream with an attached .name attribute for filename detection."""
    buf = io.BytesIO(content)
    buf.name = filename
    return buf


def build_full_analysis_payload(
    df: pd.DataFrame,
    filename: str,
    format_type: str = "CSV",
    active_worksheet: Optional[str] = None,
    workbook_meta: Optional[WorkbookMetadata] = None,
) -> dict[str, Any]:
    """Execute complete analytical pipeline across overview, quality, stats, charts, and outliers."""
    # 1. Dataset Overview
    overview = get_dataset_overview(df)
    meta_df = get_column_metadata(df)

    # 2. Data Preview (first 50 rows)
    preview_rows = df.head(50).replace({np.nan: None}).to_dict(orient="records")

    # 3. Data Quality Audit
    quality = generate_data_quality_report(df)

    # 4. Numeric & Categorical Statistics
    num_stats_df = get_numeric_statistics(df)
    num_stats_dict = num_stats_df.to_dict(orient="records") if not num_stats_df.empty else []

    cat_stats_map = {}
    for col in overview.categorical_columns:
        c_stats = get_categorical_statistics(df, col, top_n=5)
        cat_stats_map[col] = {
            "unique_count": c_stats.unique_count,
            "most_frequent_value": c_stats.most_frequent_value,
            "frequency_table": c_stats.frequency_table.to_dict(orient="records"),
        }

    # 5. Interactive Visualizations (serialized Plotly figures)
    visualizations = {}
    try:
        mv_fig = create_missing_values_bar_chart(df)
        visualizations["missing_values"] = json.loads(mv_fig.to_json())
    except Exception:
        visualizations["missing_values"] = None

    histograms = {}
    box_plots = {}
    for col in overview.numeric_columns:
        try:
            h_fig = create_histogram(df, col)
            histograms[col] = json.loads(h_fig.to_json())
        except Exception:
            histograms[col] = None

        try:
            b_fig = create_box_plot(df, col)
            box_plots[col] = json.loads(b_fig.to_json())
        except Exception:
            box_plots[col] = None

    visualizations["histograms"] = histograms
    visualizations["box_plots"] = box_plots

    category_bars = {}
    for col in overview.categorical_columns:
        try:
            cb_fig = create_categorical_bar_chart(df, col, top_n=8)
            category_bars[col] = json.loads(cb_fig.to_json())
        except Exception:
            category_bars[col] = None
    visualizations["category_bars"] = category_bars

    if len(overview.numeric_columns) >= 2:
        try:
            corr_fig = create_correlation_heatmap(df, columns=overview.numeric_columns[:10])
            visualizations["correlation_heatmap"] = json.loads(corr_fig.to_json())
        except Exception:
            visualizations["correlation_heatmap"] = None
    else:
        visualizations["correlation_heatmap"] = None

    # 6. Outlier Analysis (Tukey IQR)
    outliers_map = {}
    for col in overview.numeric_columns:
        try:
            res = detect_outliers_iqr(df, col, multiplier=1.5)
            outliers_map[col] = {
                "column": res.column,
                "valid_observations_count": res.valid_observations_count,
                "q1": res.q1,
                "q3": res.q3,
                "iqr": res.iqr,
                "multiplier": res.multiplier,
                "lower_bound": res.lower_bound,
                "upper_bound": res.upper_bound,
                "flagged_count": res.flagged_count,
                "lower_outliers_count": res.lower_outliers_count,
                "upper_outliers_count": res.upper_outliers_count,
                "flagged_pct": res.flagged_pct,
                "status_message": res.status_message,
                "flagged_preview": res.flagged_df.head(20).replace({np.nan: None}).to_dict(orient="records"),
            }
        except Exception:
            outliers_map[col] = None

    # Assembled response
    payload = {
        "dataset_name": filename,
        "dataset_format": format_type,
        "active_worksheet": active_worksheet,
        "workbook_metadata": (
            {
                "file_format": workbook_meta.file_format,
                "total_sheets": workbook_meta.total_sheets,
                "sheet_names": workbook_meta.sheet_names,
                "sheets": [
                    {
                        "name": s.name,
                        "row_count": s.row_count,
                        "col_count": s.col_count,
                        "sample_headers": s.sample_headers,
                        "is_empty": s.is_empty,
                    }
                    for s in workbook_meta.sheets
                ],
            }
            if workbook_meta
            else None
        ),
        "overview": {
            "total_rows": overview.total_rows,
            "total_columns": overview.total_columns,
            "total_cells": overview.total_cells,
            "memory_usage_bytes": overview.memory_usage_bytes,
            "memory_usage_formatted": overview.memory_usage_formatted,
            "total_duplicate_rows": overview.total_duplicate_rows,
            "duplicate_rows_pct": overview.duplicate_rows_pct,
            "total_missing_cells": overview.total_missing_cells,
            "missing_cells_pct": overview.missing_cells_pct,
            "numeric_columns": overview.numeric_columns,
            "categorical_columns": overview.categorical_columns,
            "datetime_columns": overview.datetime_columns,
            "boolean_columns": overview.boolean_columns,
        },
        "columns": meta_df.to_dict(orient="records"),
        "preview": preview_rows,
        "quality": {
            "status": quality.status,
            "overall_health_score": quality.overall_health_score,
            "issues": [
                {
                    "title": iss.title,
                    "description": iss.description,
                    "severity": iss.severity.value if hasattr(iss.severity, "value") else str(iss.severity),
                    "affected_columns": iss.affected_columns,
                }
                for iss in quality.issues
            ],
            "missing_summary": {
                "total_missing_cells": quality.missing_summary.total_missing_cells,
                "missing_cells_pct": quality.missing_summary.missing_cells_pct,
                "columns_with_missing_count": quality.missing_summary.columns_with_missing_count,
                "detail_table": quality.missing_summary.detail_table.to_dict(orient="records"),
            },
            "duplicate_summary": {
                "total_duplicates": quality.duplicate_summary.total_duplicates,
                "duplicate_pct": quality.duplicate_summary.duplicate_pct,
                "rows_remaining_after_dedup": quality.duplicate_summary.rows_remaining_after_dedup,
                "preview": quality.duplicate_summary.duplicate_rows_preview.head(20).replace({np.nan: None}).to_dict(orient="records"),
            },
            "variance_summary": {
                "constant_columns": quality.variance_summary.constant_columns,
                "entirely_empty_columns": quality.variance_summary.entirely_empty_columns,
                "nearly_empty_columns": quality.variance_summary.nearly_empty_columns,
                "threshold_pct": quality.variance_summary.threshold_pct,
            },
        },
        "numeric_statistics": num_stats_dict,
        "categorical_statistics": cat_stats_map,
        "visualizations": visualizations,
        "outliers": outliers_map,
    }

    return sanitize_for_json(payload)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    """Health check endpoint confirming API status."""
    return {"status": "ok", "app": "Analytix", "version": "2.0.0"}


@app.get("/api/sample/csv")
def load_sample_csv() -> dict[str, Any]:
    """Analyze the built-in Superstore EDA sample CSV dataset."""
    if not SAMPLE_CSV_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample CSV file not found on server.",
        )
    result = load_csv_detailed(SAMPLE_CSV_PATH)
    return build_full_analysis_payload(result.df, filename="sample_superstore_eda.csv", format_type="CSV")


@app.get("/api/sample/excel")
def load_sample_excel() -> dict[str, Any]:
    """Analyze the built-in multi-sheet Excel sample workbook."""
    if not SAMPLE_EXCEL_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample Excel file not found on server.",
        )
    workbook_meta = inspect_excel_workbook(SAMPLE_EXCEL_PATH)
    active_sheet = workbook_meta.sheet_names[0]
    load_res = load_excel_sheet(SAMPLE_EXCEL_PATH, active_sheet)
    format_label = f"Excel ({workbook_meta.file_format})"
    return build_full_analysis_payload(
        load_res.df,
        filename="sample_analytix_multisheet.xlsx",
        format_type=format_label,
        active_worksheet=active_sheet,
        workbook_meta=workbook_meta,
    )


@app.post("/api/upload/csv")
async def upload_csv(file: UploadFile = File(...)) -> dict[str, Any]:
    """Upload and analyze a CSV dataset within Vercel serverless limits."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name.")

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported by this endpoint.")

    content = await file.read()
    if len(content) > MAX_SERVERLESS_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds Vercel's 4.5 MB serverless upload limit ({len(content)/(1024*1024):.1f} MB uploaded). Please upload a file under 4.5 MB.",
        )

    buf = _create_named_buffer(content, file.filename)
    try:
        res = load_csv_detailed(buf)
    except CSVEmptyError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except (CSVEncodingError, CSVParsingError, CSVSizeLimitExceededError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(exc)}")

    return build_full_analysis_payload(res.df, filename=file.filename, format_type="CSV")


@app.post("/api/upload/excel/inspect")
async def inspect_excel(file: UploadFile = File(...)) -> dict[str, Any]:
    """Inspect Excel workbook metadata and discover all worksheets."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name.")

    lower = file.filename.lower()
    if not (lower.endswith(".xlsx") or lower.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Only .xlsx and .xls Excel workbooks are supported.")

    content = await file.read()
    if len(content) > MAX_SERVERLESS_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds Vercel's 4.5 MB serverless upload limit ({len(content)/(1024*1024):.1f} MB uploaded).",
        )

    buf = _create_named_buffer(content, file.filename)
    try:
        workbook_meta = inspect_excel_workbook(buf)
    except (ExcelCorruptedError, ExcelEmptyWorkbookError, ExcelUnsupportedFormatError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to inspect Excel workbook: {str(exc)}")

    return sanitize_for_json(
        {
            "filename": file.filename,
            "file_format": workbook_meta.file_format,
            "total_sheets": workbook_meta.total_sheets,
            "sheet_names": workbook_meta.sheet_names,
            "sheets": [
                {
                    "name": s.name,
                    "row_count": s.row_count,
                    "col_count": s.col_count,
                    "sample_headers": s.sample_headers,
                    "is_empty": s.is_empty,
                }
                for s in workbook_meta.sheets
            ],
        }
    )


@app.post("/api/upload/excel/sheet")
async def load_excel_worksheet(
    file: UploadFile = File(...),
    sheet_name: str = Form(...),
) -> dict[str, Any]:
    """Load and analyze a specific worksheet from an uploaded Excel workbook."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name.")

    content = await file.read()
    if len(content) > MAX_SERVERLESS_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds Vercel's 4.5 MB serverless upload limit ({len(content)/(1024*1024):.1f} MB uploaded).",
        )

    buf_inspect = _create_named_buffer(content, file.filename)
    buf_load = _create_named_buffer(content, file.filename)
    try:
        workbook_meta = inspect_excel_workbook(buf_inspect)
        load_res = load_excel_sheet(buf_load, sheet_name=sheet_name)
    except (
        ExcelSheetNotFoundError,
        ExcelEmptySheetError,
        ExcelCorruptedError,
        ExcelUnsupportedFormatError,
    ) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load worksheet: {str(exc)}")

    format_label = f"Excel ({workbook_meta.file_format})"
    return build_full_analysis_payload(
        load_res.df,
        filename=file.filename,
        format_type=format_label,
        active_worksheet=sheet_name,
        workbook_meta=workbook_meta,
    )


class OutlierRecalcRequest(BaseModel):
    data: list[dict[str, Any]]
    column: str
    multiplier: float = 1.5


@app.post("/api/analysis/outliers")
def recalculate_outliers(req: OutlierRecalcRequest) -> dict[str, Any]:
    """Recalculate IQR outliers with a custom multiplier slider value."""
    if not req.data:
        raise HTTPException(status_code=400, detail="No data provided for outlier calculation.")

    df = pd.DataFrame(req.data)
    if req.column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{req.column}' not in dataset.")

    try:
        res = detect_outliers_iqr(df, req.column, multiplier=req.multiplier)
        return sanitize_for_json(
            {
                "column": res.column,
                "valid_observations_count": res.valid_observations_count,
                "q1": res.q1,
                "q3": res.q3,
                "iqr": res.iqr,
                "multiplier": res.multiplier,
                "lower_bound": res.lower_bound,
                "upper_bound": res.upper_bound,
                "flagged_count": res.flagged_count,
                "lower_outliers_count": res.lower_outliers_count,
                "upper_outliers_count": res.upper_outliers_count,
                "flagged_pct": res.flagged_pct,
                "status_message": res.status_message,
                "flagged_preview": res.flagged_df.head(50).replace({np.nan: None}).to_dict(orient="records"),
            }
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


class HistogramRequest(BaseModel):
    data: list[dict[str, Any]]
    column: str
    nbins: int = 30


@app.post("/api/analysis/histogram")
def recalculate_histogram(req: HistogramRequest) -> dict[str, Any]:
    """Generate dynamic histogram with configured bin count."""
    df = pd.DataFrame(req.data)
    if req.column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{req.column}' not found.")
    fig = create_histogram(df, req.column, nbins=req.nbins)
    return sanitize_for_json(json.loads(fig.to_json()))


class CorrelationRequest(BaseModel):
    data: list[dict[str, Any]]
    columns: list[str]
    method: str = "pearson"


@app.post("/api/analysis/correlation")
def recalculate_correlation(req: CorrelationRequest) -> dict[str, Any]:
    """Generate dynamic correlation heatmap for selected columns."""
    df = pd.DataFrame(req.data)
    fig = create_correlation_heatmap(df, columns=req.columns, method=req.method)
    return sanitize_for_json(json.loads(fig.to_json()))


class ExportCSVRequest(BaseModel):
    rows: list[dict[str, Any]]
    filename: str = "analytix_export.csv"


@app.post("/api/export/csv")
def export_csv(req: ExportCSVRequest) -> Response:
    """Export tabular rows to standardized CSV bytes."""
    df = pd.DataFrame(req.rows)
    csv_bytes = export_dataframe_to_csv(df)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{req.filename}"'},
    )


class ExportJSONRequest(BaseModel):
    filename: str
    dataset_format: str = "CSV"
    active_worksheet: Optional[str] = None
    overview: dict[str, Any]
    columns: list[dict[str, Any]]
    quality: dict[str, Any]
    numeric_stats: Optional[list[dict[str, Any]]] = None


@app.post("/api/export/json")
def export_json(req: ExportJSONRequest) -> Response:
    """Generate consolidated, JSON-safe analytical audit report."""
    columns_df = pd.DataFrame(req.columns) if req.columns else None
    numeric_stats_df = pd.DataFrame(req.numeric_stats) if req.numeric_stats else None

    report_str = generate_json_report(
        filename=req.filename,
        overview_dict=req.overview,
        column_metadata_df=columns_df,
        quality_summary_dict=req.quality,
        numeric_stats_df=numeric_stats_df,
        dataset_format=req.dataset_format,
        active_worksheet=req.active_worksheet,
    )

    clean_name = req.filename.replace(".csv", "").replace(".xlsx", "").replace(".xls", "")
    if req.active_worksheet:
        clean_name += f"_{req.active_worksheet}"
    download_filename = f"{clean_name}_eda_report.json"

    return Response(
        content=report_str.encode("utf-8"),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{download_filename}"'},
    )
