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
