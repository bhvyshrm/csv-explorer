"""Unit and integration tests for Analytix FastAPI serverless endpoints."""

import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from api.index import app, MAX_SERVERLESS_BYTES

client = TestClient(app)


def test_health_check():
    """Verify health check endpoint returns 200 OK and expected metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "Analytix"
    assert data["version"] == "2.0.0"


def test_sample_csv_endpoint():
    """Verify built-in sample CSV dataset analysis."""
    response = client.get("/api/sample/csv")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset_name"] == "sample_superstore_eda.csv"
    assert data["dataset_format"] == "CSV"
    assert data["overview"]["total_rows"] == 122
    assert data["overview"]["total_columns"] == 16
    assert "Sales" in data["overview"]["numeric_columns"]
    assert len(data["columns"]) == 16
    assert len(data["preview"]) > 0
    assert data["quality"]["overall_health_score"] > 0
    assert "missing_values" in data["visualizations"]
    assert "Sales" in data["outliers"]
    assert data["outliers"]["Sales"]["flagged_count"] >= 2


def test_sample_excel_endpoint():
    """Verify built-in sample Excel workbook analysis and sheet discovery."""
    response = client.get("/api/sample/excel")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset_name"] == "sample_analytix_multisheet.xlsx"
    assert data["dataset_format"] in ["Excel (.xlsx)", "Excel (.xls)"]
    assert data["active_worksheet"] == "Orders_Data"
    assert data["workbook_metadata"] is not None
    assert len(data["workbook_metadata"]["sheet_names"]) == 3
    assert "Customer_Demographics" in data["workbook_metadata"]["sheet_names"]
    assert data["overview"]["total_rows"] > 0


def test_upload_csv_valid():
    """Verify valid CSV upload and instant end-to-end analysis."""
    csv_content = b"ID,Name,Score,Category\n1,Alice,95.5,Eng\n2,Bob,88.0,Math\n3,Charlie,72.5,Eng\n"
    files = {"file": ("students.csv", io.BytesIO(csv_content), "text/csv")}
    response = client.post("/api/upload/csv", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["dataset_name"] == "students.csv"
    assert data["overview"]["total_rows"] == 3
    assert data["overview"]["total_columns"] == 4
    assert "Score" in data["overview"]["numeric_columns"]


def test_upload_csv_empty():
    """Verify empty CSV returns 400 Bad Request."""
    files = {"file": ("empty.csv", io.BytesIO(b""), "text/csv")}
    response = client.post("/api/upload/csv", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_csv_oversized():
    """Verify oversized file returns 413 Payload Too Large."""
    oversized = b"a" * (MAX_SERVERLESS_BYTES + 1024)
    files = {"file": ("large.csv", io.BytesIO(oversized), "text/csv")}
    response = client.post("/api/upload/csv", files=files)
    assert response.status_code == 413
    assert "4.5 mb" in response.json()["detail"].lower()


def test_upload_excel_inspect_and_sheet_selection():
    """Verify workbook inspection and subsequent sheet analysis."""
    sample_excel = Path("sample_data/sample_analytix_multisheet.xlsx")
    assert sample_excel.exists()

    with open(sample_excel, "rb") as f:
        excel_bytes = f.read()

    # 1. Inspect workbook
    inspect_resp = client.post(
        "/api/upload/excel/inspect",
        files={"file": ("test_multisheet.xlsx", io.BytesIO(excel_bytes), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert inspect_resp.status_code == 200
    meta = inspect_resp.json()
    assert meta["total_sheets"] == 3
    assert "Empty_Template" in meta["sheet_names"]

    # 2. Load second sheet Customer_Demographics
    sheet_resp = client.post(
        "/api/upload/excel/sheet",
        files={"file": ("test_multisheet.xlsx", io.BytesIO(excel_bytes), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"sheet_name": "Customer_Demographics"},
    )
    assert sheet_resp.status_code == 200
    sheet_data = sheet_resp.json()
    assert sheet_data["active_worksheet"] == "Customer_Demographics"
    assert sheet_data["overview"]["total_rows"] == 50


def test_recalculate_outliers_endpoint():
    """Verify IQR outlier recalculation with custom multiplier."""
    payload = {
        "data": [
            {"val": 10}, {"val": 12}, {"val": 11}, {"val": 13}, {"val": 12},
            {"val": 100},  # outlier
        ],
        "column": "val",
        "multiplier": 1.5,
    }
    response = client.post("/api/analysis/outliers", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["flagged_count"] == 1
    assert data["upper_outliers_count"] == 1


def test_export_csv_and_json_endpoints():
    """Verify CSV and JSON report export endpoints."""
    # CSV export
    csv_payload = {
        "rows": [{"col1": "A", "col2": 1}, {"col1": "B", "col2": 2}],
        "filename": "test_export.csv",
    }
    csv_resp = client.post("/api/export/csv", json=csv_payload)
    assert csv_resp.status_code == 200
    assert b"col1,col2" in csv_resp.content

    # JSON export
    json_payload = {
        "filename": "test.csv",
        "dataset_format": "CSV",
        "overview": {"total_rows": 2, "total_columns": 2},
        "columns": [{"Column Name": "col1", "Inferred Type": "Categorical"}],
        "quality": {"status": "No major issues detected"},
        "numeric_stats": None,
    }
    json_resp = client.post("/api/export/json", json=json_payload)
    assert json_resp.status_code == 200
    assert b"Analytix" in json_resp.content
    assert b"test.csv" in json_resp.content


def test_root_and_base_api_endpoints():
    """Verify root / and base /api and /api/ return 200 OK without 404 detail not found."""
    for path in ["/", "/api", "/api/"]:
        resp = client.get(path)
        assert resp.status_code == 200, f"Failed for path {path}"
        data = resp.json()
        assert data["status"] == "ok"
        assert data["app"] == "Analytix"
        assert data["version"] == "2.0.0"


def test_routes_without_api_prefix():
    """Verify routes resolve successfully without /api prefix (supporting direct Vercel function mapping)."""
    # 1. Health check without prefix
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "ok"

    # 2. Sample CSV without prefix
    csv_resp = client.get("/sample/csv")
    assert csv_resp.status_code == 200
    assert csv_resp.json()["dataset_name"] == "sample_superstore_eda.csv"

    # 3. Sample Excel without prefix
    excel_resp = client.get("/sample/excel")
    assert excel_resp.status_code == 200
    assert excel_resp.json()["dataset_name"] == "sample_analytix_multisheet.xlsx"


def test_invalid_requests_and_structured_error_responses():
    """Verify invalid requests return valid JSON error responses with meaningful detail."""
    # Non-existent endpoint produces standard 404 with detail
    res_404 = client.get("/api/nonexistent_route_test")
    assert res_404.status_code == 404
    assert "detail" in res_404.json()

    # Invalid file format produces 400 with string detail
    files = {"file": ("data.txt", io.BytesIO(b"hello world"), "text/plain")}
    res_bad_format = client.post("/api/upload/csv", files=files)
    assert res_bad_format.status_code == 400
    assert "detail" in res_bad_format.json()
    assert ".csv" in res_bad_format.json()["detail"].lower()

    # Outliers calculation with missing column produces 400 with detail
    bad_outlier_payload = {
        "data": [{"a": 1}, {"a": 2}],
        "column": "non_existent_column",
        "multiplier": 1.5,
    }
    res_bad_outlier = client.post("/api/analysis/outliers", json=bad_outlier_payload)
    assert res_bad_outlier.status_code == 400
    assert "detail" in res_bad_outlier.json()
    assert "non_existent_column" in res_bad_outlier.json()["detail"]


def test_vercel_routing_middleware_restores_path():
    """Verify ASGI middleware restores original path when Vercel rewrites to /api/index.py."""
    # 1. Health check via Vercel rewrite with x-matched-path
    res_health = client.get("/api/index.py", headers={"x-matched-path": "/api/health"})
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    # 2. Sample CSV via Vercel rewrite with x-matched-path
    res_csv = client.get("/api/index.py", headers={"x-matched-path": "/api/sample/csv"})
    assert res_csv.status_code == 200
    assert res_csv.json()["dataset_name"] == "sample_superstore_eda.csv"

    # 3. Sample Excel via Vercel rewrite with x-matched-path
    res_excel = client.get("/api/index.py", headers={"x-matched-path": "/api/sample/excel"})
    assert res_excel.status_code == 200
    assert res_excel.json()["dataset_name"] == "sample_analytix_multisheet.xlsx"

    # 4. Supports x-vercel-matched-path header fallback
    res_alt_hdr = client.get("/api/index.py", headers={"x-vercel-matched-path": "/api/health"})
    assert res_alt_hdr.status_code == 200
    assert res_alt_hdr.json()["status"] == "ok"

    # 5. Supports x-forwarded-uri header fallback
    res_fwd_uri = client.get("/api/index.py", headers={"x-forwarded-uri": "/api/health"})
    assert res_fwd_uri.status_code == 200
    assert res_fwd_uri.json()["status"] == "ok"

    # 6. Strips query parameters from matched path gracefully
    res_with_query = client.get("/api/index.py", headers={"x-matched-path": "/api/sample/csv?v=2"})
    assert res_with_query.status_code == 200
    assert res_with_query.json()["dataset_name"] == "sample_superstore_eda.csv"

    # 7. Direct hit on /api/index.py without proxy headers
    res_direct = client.get("/api/index.py")
    assert res_direct.status_code == 200
    assert res_direct.json()["status"] == "ok"

    # 8. Direct hit on /api/index
    res_index = client.get("/api/index")
    assert res_index.status_code == 200
    assert res_index.json()["status"] == "ok"


def test_formats_endpoint():
    """Verify formats registry endpoint returns full capability list."""
    response = client.get("/api/formats")
    assert response.status_code == 200
    formats = response.json()
    assert len(formats) >= 7
    ids = [f["id"] for f in formats]
    assert "csv" in ids
    assert "json" in ids
    assert "parquet" in ids
    assert "text-log" in ids


def test_samples_catalog_endpoint():
    """Verify sample datasets catalog endpoint returns metadata."""
    response = client.get("/api/samples")
    assert response.status_code == 200
    samples = response.json()
    assert len(samples) >= 5
    formats = [s["format"] for s in samples]
    assert "CSV" in formats
    assert "JSON" in formats
    assert "TSV" in formats


def test_new_sample_datasets():
    """Verify all new sample dataset endpoints load and analyze successfully."""
    # JSON sample
    res_json = client.get("/api/sample/json")
    assert res_json.status_code == 200
    assert res_json.json()["dataset_format"] == "JSON"
    assert res_json.json()["overview"]["total_rows"] > 0

    # TSV sample
    res_tsv = client.get("/api/sample/tsv")
    assert res_tsv.status_code == 200
    assert res_tsv.json()["dataset_format"] == "TSV"
    assert res_tsv.json()["overview"]["total_rows"] > 0

    # Log sample
    res_log = client.get("/api/sample/log")
    assert res_log.status_code == 200
    assert res_log.json()["dataset_format"] in ["Log", "Text"]
    assert res_log.json()["overview"]["total_rows"] > 0

    # Parquet sample
    res_parquet = client.get("/api/sample/parquet")
    assert res_parquet.status_code == 200
    assert res_parquet.json()["dataset_format"] == "Parquet"
    assert res_parquet.json()["overview"]["total_rows"] > 0


def test_universal_upload_endpoint():
    """Verify universal upload endpoint ingests diverse formats (.json, .tsv)."""
    # 1. Upload JSON
    json_bytes = b'[{"item": "Keyboard", "price": 49.99}, {"item": "Mouse", "price": 24.50}]'
    res_json = client.post(
        "/api/upload",
        files={"file": ("inventory.json", io.BytesIO(json_bytes), "application/json")},
    )
    assert res_json.status_code == 200
    data_json = res_json.json()
    assert data_json["dataset_format"] == "JSON"
    assert data_json["overview"]["total_rows"] == 2

    # 2. Upload TSV
    tsv_bytes = b"user\trole\nalice\tadmin\nbob\tanalyst\n"
    res_tsv = client.post(
        "/api/upload",
        files={"file": ("roles.tsv", io.BytesIO(tsv_bytes), "text/tab-separated-values")},
    )
    assert res_tsv.status_code == 200
    data_tsv = res_tsv.json()
    assert data_tsv["dataset_format"] == "TSV"
    assert data_tsv["overview"]["total_rows"] == 2


def test_export_xlsx_and_zip_endpoints():
    """Verify XLSX workbook and Complete ZIP archive export endpoints."""
    payload = {
        "filename": "orders.csv",
        "dataset_format": "CSV",
        "overview": {
            "total_rows": 10,
            "total_columns": 2,
            "total_cells": 20,
            "memory_usage_formatted": "2.4 KB",
            "total_duplicate_rows": 0,
            "duplicate_rows_pct": 0.0,
            "total_missing_cells": 0,
            "missing_cells_pct": 0.0,
            "numeric_columns": ["Amount"],
            "categorical_columns": ["Region"],
        },
        "columns": [
            {
                "Column Name": "Amount",
                "Inferred Type": "Numeric",
                "Python dtype": "float64",
                "Missing Count": 0,
                "Missing %": 0.0,
                "Unique Values": 10,
                "Memory (Bytes)": 80,
            }
        ],
        "quality": {
            "status": "Healthy",
            "overall_health_score": 100.0,
            "missing_summary": {"detail_table": []},
        },
        "numeric_stats": [{"Statistic": "mean", "Amount": 150.0}],
    }

    # 1. Test /api/export/xlsx
    res_xlsx = client.post("/api/export/xlsx", json=payload)
    assert res_xlsx.status_code == 200
    assert "spreadsheetml.sheet" in res_xlsx.headers["content-type"]
    assert len(res_xlsx.content) > 0

    # 2. Test /api/export/zip
    zip_payload = {**payload, "preview": [{"Amount": 100, "Region": "North"}]}
    res_zip = client.post("/api/export/zip", json=zip_payload)
    assert res_zip.status_code == 200
    assert "application/zip" in res_zip.headers["content-type"]
    assert len(res_zip.content) > 0

    # 3. Test /api/export/html
    res_html = client.post("/api/export/html", json=payload)
    assert res_html.status_code == 200
    assert "text/html" in res_html.headers["content-type"]
    assert b"Executive Analysis Report" in res_html.content

