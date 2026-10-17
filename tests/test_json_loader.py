"""Unit tests for Analytix JSON and NDJSON / JSONL loader."""

import io
import pytest
import pandas as pd

from src.json_loader import (
    JSONEmptyError,
    JSONParsingError,
    load_json_detailed,
    load_ndjson_detailed,
)


def test_load_json_array_of_objects():
    """Verify loading standard array of objects."""
    json_bytes = b'[{"id": 1, "product": "Widget", "price": 19.99}, {"id": 2, "product": "Gadget", "price": 29.50}]'
    res = load_json_detailed(io.BytesIO(json_bytes))
    assert len(res.df) == 2
    assert list(res.df.columns) == ["id", "product", "price"]
    assert res.df["price"].iloc[0] == 19.99


def test_load_json_nested_flattening():
    """Verify nested JSON objects are flattened with dot notation."""
    json_bytes = b'[{"user": {"name": "Alice", "city": "NY"}, "score": 95}, {"user": {"name": "Bob", "city": "SF"}, "score": 88}]'
    res = load_json_detailed(io.BytesIO(json_bytes))
    assert len(res.df) == 2
    assert "user.name" in res.df.columns
    assert "user.city" in res.df.columns
    assert res.df["user.name"].iloc[0] == "Alice"
    assert any("flattened" in w.lower() for w in res.metadata.warnings)


def test_load_json_wrapped_records():
    """Verify loading JSON where records are inside a container key like 'data'."""
    json_bytes = b'{"status": "ok", "data": [{"id": 101, "val": "A"}, {"id": 102, "val": "B"}]}'
    res = load_json_detailed(io.BytesIO(json_bytes))
    assert len(res.df) == 2
    assert list(res.df.columns) == ["id", "val"]


def test_load_json_empty_error():
    """Verify empty JSON content raises JSONEmptyError."""
    with pytest.raises(JSONEmptyError):
        load_json_detailed(io.BytesIO(b""))

    with pytest.raises(JSONEmptyError):
        load_json_detailed(io.BytesIO(b"[]"))


def test_load_json_invalid_syntax():
    """Verify malformed JSON raises JSONParsingError with line/col details."""
    with pytest.raises(JSONParsingError) as exc_info:
        load_json_detailed(io.BytesIO(b'{"key": 123,'))
    assert "invalid json" in str(exc_info.value).lower()


def test_load_ndjson_valid():
    """Verify loading valid NDJSON / JSONL records."""
    ndjson_bytes = b'{"user_id": 1, "event": "login"}\n{"user_id": 2, "event": "signup"}\n{"user_id": 1, "event": "checkout"}\n'
    res = load_ndjson_detailed(io.BytesIO(ndjson_bytes))
    assert len(res.df) == 3
    assert list(res.df.columns) == ["user_id", "event"]
    assert res.df["event"].iloc[1] == "signup"


def test_load_ndjson_with_bad_lines_warns():
    """Verify NDJSON skips invalid lines and records warnings."""
    ndjson_bytes = b'{"a": 1}\nNOT_VALID_JSON\n{"a": 2}\n'
    res = load_ndjson_detailed(io.BytesIO(ndjson_bytes))
    assert len(res.df) == 2
    assert any("invalid" in w.lower() for w in res.metadata.warnings)
