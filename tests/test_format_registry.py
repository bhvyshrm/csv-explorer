"""Unit tests for Analytix multi-format registry and dispatcher."""

import io
import pytest

from src.format_registry import (
    SUPPORTED_FORMATS,
    UnsupportedFormatError,
    detect_and_load_file,
)


def test_format_registry_descriptors():
    """Verify descriptors expose all key formats and accurate availability status."""
    ids = [f.id for f in SUPPORTED_FORMATS]
    assert "csv" in ids
    assert "excel" in ids
    assert "json" in ids
    assert "parquet" in ids
    assert "text-log" in ids
    assert "tsv" in ids
    assert "xml" in ids
    assert "database" in ids

    db_descriptor = next(f for f in SUPPORTED_FORMATS if f.id == "database")
    assert not db_descriptor.is_available
    assert db_descriptor.status_label == "Coming soon"


def test_detect_and_load_csv():
    """Verify CSV format detection via registry."""
    buf = io.BytesIO(b"colA,colB\n1,2\n")
    res = detect_and_load_file(buf, filename="data.csv")
    assert res.format_type == "CSV"
    assert len(res.df) == 1


def test_detect_and_load_tsv():
    """Verify TSV format detection via registry."""
    buf = io.BytesIO(b"colA\tcolB\n1\t2\n")
    res = detect_and_load_file(buf, filename="data.tsv")
    assert res.format_type == "TSV"
    assert len(res.df) == 1


def test_detect_and_load_json():
    """Verify JSON format detection via registry."""
    buf = io.BytesIO(b'[{"x": 10, "y": 20}]')
    res = detect_and_load_file(buf, filename="data.json")
    assert res.format_type == "JSON"
    assert len(res.df) == 1


def test_unsupported_format_error():
    """Verify unsupported file extensions are safely rejected."""
    buf = io.BytesIO(b"test binary content")
    with pytest.raises(UnsupportedFormatError) as exc_info:
        detect_and_load_file(buf, filename="document.pdf")
    assert "unsupported file format '.pdf'" in str(exc_info.value).lower()
