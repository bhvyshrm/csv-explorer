"""JSON, JSON Lines, and NDJSON ingestion and normalization for Analytix.

Provides robust handling for:
- JSON arrays of records: `[{"id": 1, "name": "A"}, ...]`
- Nested JSON structures automatically flattened with dot notation (`user.name`)
- Top-level wrapper objects: `{"data": [...]}`, `{"records": [...]}`, `{"items": [...]}`
- Newline-Delimited JSON (NDJSON / JSONL): one valid JSON object per line
- Corrupted line reporting and malformed structure diagnostics
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any, BinaryIO, Union

import pandas as pd

from src.data_loader import (
    DEFAULT_MAX_FILE_SIZE_BYTES,
    CSVExplorerError,
    LoadMetadata,
    LoadResult,
    _extract_file_bytes,
)


class JSONExplorerError(CSVExplorerError):
    """Base exception for JSON ingestion."""
    pass


class JSONEmptyError(JSONExplorerError):
    """Raised when JSON content is empty or contains no records."""
    pass


class JSONParsingError(JSONExplorerError):
    """Raised when JSON syntax is malformed or invalid."""
    pass


def _flatten_or_normalize(data: Any) -> tuple[pd.DataFrame, list[str]]:
    """Convert parsed JSON data structures into a normalized 2D DataFrame.

    Returns:
        tuple[pd.DataFrame, list[str]]: DataFrame and any conversion warnings.
    """
    warnings: list[str] = []

    if isinstance(data, list):
        if not data:
            raise JSONEmptyError("The JSON file contains an empty array (`[]`).")

        # If array of primitives, turn into a single column
        if not isinstance(data[0], dict):
            df = pd.DataFrame({"value": data})
            return df, warnings

        # Flatten nested dictionaries
        df = pd.json_normalize(data)
        if any("." in col for col in df.columns):
            warnings.append("Nested JSON structures detected and flattened using dot notation.")
        return df, warnings

    if isinstance(data, dict):
        if not data:
            raise JSONEmptyError("The JSON file contains an empty object (`{}`).")

        # Check for common container keys
        for key in ["data", "records", "items", "results", "rows", "values"]:
            if key in data and isinstance(data[key], list) and len(data[key]) > 0:
                warnings.append(f"Extracted tabular records from root container key '{key}'.")
                return _flatten_or_normalize(data[key])

        # Check if dictionary of lists (column-oriented JSON)
        if all(isinstance(v, list) for v in data.values()) and len(data) > 0:
            try:
                df = pd.DataFrame(data)
                return df, warnings
            except Exception:
                pass

        # Single record dictionary
        df = pd.json_normalize([data])
        warnings.append("Single JSON object loaded as a single-row dataset.")
        return df, warnings

    raise JSONParsingError("Top-level JSON must be an array of objects or an object containing records.")


def load_json_detailed(
    file_input: Union[str, Path, BinaryIO, io.BytesIO, Any],
    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> LoadResult:
    """Load, parse, and normalize standard JSON files into a tabular DataFrame.

    Args:
        file_input: File path, BytesIO, or file-like object.
        max_size_bytes: Maximum allowed file size in bytes.

    Returns:
        LoadResult: Parsed DataFrame and ingestion metadata.
    """
    raw_bytes, filename = _extract_file_bytes(file_input, max_size_bytes)

    if len(raw_bytes) == 0 or not raw_bytes.strip():
        raise JSONEmptyError(f"The JSON file '{filename}' is empty (0 bytes).")

    try:
        decoded_text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            decoded_text = raw_bytes.decode("latin1")
        except Exception as exc:
            raise JSONParsingError(f"Failed to decode JSON content: {str(exc)}") from exc

    try:
        parsed_json = json.loads(decoded_text)
    except json.JSONDecodeError as exc:
        raise JSONParsingError(
            f"Invalid JSON syntax in '{filename}' at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    df, warnings = _flatten_or_normalize(parsed_json)
    if df.empty:
        raise JSONEmptyError(f"The JSON file '{filename}' contains no data records.")

    original_cols = [str(c) for c in df.columns]
    metadata = LoadMetadata(
        filename=filename,
        file_size_bytes=len(raw_bytes),
        encoding_used="utf-8",
        warnings=warnings,
        has_headers_only=len(df) == 0,
        original_column_names=original_cols,
    )
    df.attrs["load_metadata"] = metadata

    return LoadResult(df=df, metadata=metadata)


def load_ndjson_detailed(
    file_input: Union[str, Path, BinaryIO, io.BytesIO, Any],
    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> LoadResult:
    """Load and parse newline-delimited JSON (NDJSON / JSONL) files.

    Args:
        file_input: File path, BytesIO, or file-like object.
        max_size_bytes: Maximum allowed file size in bytes.

    Returns:
        LoadResult: Parsed DataFrame and ingestion metadata.
    """
    raw_bytes, filename = _extract_file_bytes(file_input, max_size_bytes)

    if len(raw_bytes) == 0 or not raw_bytes.strip():
        raise JSONEmptyError(f"The NDJSON file '{filename}' is empty (0 bytes).")

    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw_bytes.decode("latin1", errors="replace")

    records: list[dict[str, Any]] = []
    invalid_line_count = 0
    warnings: list[str] = []

    for line_idx, line in enumerate(text.splitlines(), start=1):
        clean_line = line.strip()
        if not clean_line:
            continue
        try:
            obj = json.loads(clean_line)
            if isinstance(obj, dict):
                records.append(obj)
            else:
                records.append({"value": obj})
        except json.JSONDecodeError:
            invalid_line_count += 1

    if not records:
        if invalid_line_count > 0:
            raise JSONParsingError(
                f"All {invalid_line_count} line(s) in '{filename}' failed JSON parsing."
            )
        raise JSONEmptyError(f"The NDJSON file '{filename}' contains zero readable records.")

    if invalid_line_count > 0:
        warnings.append(
            f"Skipped {invalid_line_count} invalid NDJSON line(s) during ingestion."
        )

    df = pd.json_normalize(records)
    if any("." in col for col in df.columns):
        warnings.append("Nested NDJSON structures detected and flattened using dot notation.")

    original_cols = [str(c) for c in df.columns]
    metadata = LoadMetadata(
        filename=filename,
        file_size_bytes=len(raw_bytes),
        encoding_used="utf-8",
        warnings=warnings,
        has_headers_only=len(df) == 0,
        original_column_names=original_cols,
    )
    df.attrs["load_metadata"] = metadata

    return LoadResult(df=df, metadata=metadata)
