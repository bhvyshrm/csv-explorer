"""Unit tests for Analytix Text and Log file loader."""

import io
import pytest

from src.text_log_loader import (
    TextLogEmptyError,
    load_text_or_log_detailed,
)


def test_load_structured_timestamp_log():
    """Verify parsing of structured timestamp log lines."""
    log_text = (
        "2026-10-17 10:00:00 [INFO] System initialized successfully\n"
        "2026-10-17 10:00:05 [WARN] High memory utilization detected (78%)\n"
        "2026-10-17 10:00:15 [ERROR] Database connection timed out on replica\n"
    ).encode("utf-8")

    res = load_text_or_log_detailed(io.BytesIO(log_text))
    assert len(res.df) == 3
    assert list(res.df.columns) == ["timestamp", "level", "message"]
    assert res.df["level"].iloc[0] == "INFO"
    assert res.df["level"].iloc[2] == "ERROR"


def test_load_web_access_log():
    """Verify parsing of Apache/Nginx web access log entries."""
    web_log = (
        '192.168.1.10 - - [17/Oct/2026:10:00:00 +0000] "GET /api/health HTTP/1.1" 200 128\n'
        '192.168.1.15 - - [17/Oct/2026:10:00:02 +0000] "POST /api/upload HTTP/1.1" 200 4096\n'
        '192.168.1.20 - - [17/Oct/2026:10:00:05 +0000] "GET /nonexistent HTTP/1.1" 404 45\n'
    ).encode("utf-8")

    res = load_text_or_log_detailed(io.BytesIO(web_log))
    assert len(res.df) == 3
    assert list(res.df.columns) == [
        "client_ip",
        "timestamp",
        "method",
        "path",
        "status_code",
        "response_size_bytes",
    ]
    assert res.df["status_code"].iloc[2] == 404


def test_load_unstructured_text_file():
    """Verify unstructured text produces line metrics table without fake columns."""
    text_content = (
        "Project Notes\n"
        "\n"
        "Antigravity redesign and expansion.\n"
        "Next steps:\n"
        "- Build report center\n"
        "- Test all formats\n"
    ).encode("utf-8")

    res = load_text_or_log_detailed(io.BytesIO(text_content))
    assert len(res.df) == 6
    assert "line_number" in res.df.columns
    assert "character_count" in res.df.columns
    assert "is_blank" in res.df.columns
    assert res.df["is_blank"].iloc[1] == True


def test_load_text_empty_error():
    """Verify empty text raises TextLogEmptyError."""
    with pytest.raises(TextLogEmptyError):
        load_text_or_log_detailed(io.BytesIO(b""))
