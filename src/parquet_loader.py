"""Parquet columnar data loader and schema inspector for Analytix.

Provides high-performance ingestion for Apache Parquet files:
- Schema discovery (column names, arrow dtypes, row groups)
- Preserves efficient columnar storage types (int32, int64, float64, categorical, timestamps)
- Dimension validation and corrupted file diagnostics
"""

from __future__ import annotations

import io
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


class ParquetExplorerError(CSVExplorerError):
    """Base exception for Parquet loading operations."""
    pass


class ParquetEmptyError(ParquetExplorerError):
    """Raised when a Parquet file contains no rows or columns."""
    pass


class ParquetParsingError(ParquetExplorerError):
    """Raised when a Parquet file is corrupted or cannot be parsed."""
    pass


def load_parquet_detailed(
    file_input: Union[str, Path, BinaryIO, io.BytesIO, Any],
    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> LoadResult:
    """Load, parse, and inspect an Apache Parquet file into a pandas DataFrame.

    Args:
        file_input: File path, BytesIO, or file-like object.
        max_size_bytes: Maximum allowed file size in bytes.

    Returns:
        LoadResult: Parsed DataFrame and ingestion metadata.
    """
    raw_bytes, filename = _extract_file_bytes(file_input, max_size_bytes)

    if len(raw_bytes) == 0:
        raise ParquetEmptyError(f"The Parquet file '{filename}' is empty (0 bytes).")

    try:
        buffer = io.BytesIO(raw_bytes)
        df = pd.read_parquet(buffer, engine="pyarrow")
    except Exception as exc:
        raise ParquetParsingError(
            f"Failed to parse Parquet file '{filename}': {str(exc)}"
        ) from exc

    if df.empty and len(df.columns) == 0:
        raise ParquetEmptyError(f"The Parquet file '{filename}' contains no rows or columns.")

    warnings: list[str] = []
    has_headers_only = len(df) == 0
    if has_headers_only:
        warnings.append("Parquet dataset contains schema definitions but zero data rows.")

    original_cols = [str(c) for c in df.columns]
    metadata = LoadMetadata(
        filename=filename,
        file_size_bytes=len(raw_bytes),
        encoding_used="parquet/binary",
        warnings=warnings,
        has_headers_only=has_headers_only,
        original_column_names=original_cols,
    )
    df.attrs["load_metadata"] = metadata

    return LoadResult(df=df, metadata=metadata)
