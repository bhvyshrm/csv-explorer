"""TSV (Tab-Separated Values) loading, parsing, and validation for Analytix.

Provides specialized handling for:
- Tab-delimited files (.tsv, .tab)
- Encodings: UTF-8, UTF-8-BOM, Latin-1, Windows-1252
- Empty files and header-only tab-separated files
- Preserves raw values, inferring standard numeric/date types safely
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any, BinaryIO, Union

import pandas as pd

from src.data_loader import (
    DEFAULT_MAX_FILE_SIZE_BYTES,
    CSVEmptyError,
    CSVExplorerError,
    CSVSizeLimitExceededError,
    LoadMetadata,
    LoadResult,
    _check_duplicate_headers,
    _extract_file_bytes,
)


class TSVExplorerError(CSVExplorerError):
    """Base exception for TSV loading operations."""
    pass


class TSVEmptyError(TSVExplorerError, CSVEmptyError):
    """Raised when a TSV file is empty."""
    pass


class TSVParsingError(TSVExplorerError):
    """Raised when a TSV file cannot be parsed."""
    pass


def load_tsv_detailed(
    file_input: Union[str, Path, BinaryIO, io.BytesIO, Any],
    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> LoadResult:
    """Load and parse a TSV file into a pandas DataFrame with comprehensive metadata.

    Args:
        file_input: File path, BytesIO, or file-like object.
        max_size_bytes: Maximum allowed file size in bytes.

    Returns:
        LoadResult: Parsed DataFrame and ingestion metadata.
    """
    raw_bytes, filename = _extract_file_bytes(file_input, max_size_bytes)
    if len(raw_bytes) == 0:
        raise TSVEmptyError(f"The TSV file '{filename}' is empty (0 bytes).")
    if len(raw_bytes.strip()) == 0:
        raise TSVEmptyError(f"The TSV file '{filename}' contains only whitespace.")

    candidate_encodings = ["utf-8-sig", "utf-8", "latin1", "cp1252", "iso-8859-1"]
    warnings: list[str] = []
    parsed_df: pd.DataFrame | None = None
    successful_encoding: str = ""

    for enc in candidate_encodings:
        try:
            text = raw_bytes.decode(enc)
            lines = [l for l in text.splitlines() if l.strip()]
            if not lines:
                raise TSVEmptyError(f"The TSV file '{filename}' contains no readable data rows.")

            dup_headers = _check_duplicate_headers(lines[0])
            if dup_headers:
                warnings.append(
                    f"Duplicate column headers detected: {dup_headers}. "
                    "Columns have been disambiguated automatically."
                )

            buffer = io.StringIO(text)
            df = pd.read_csv(buffer, sep="\t", low_memory=False)
            successful_encoding = enc
            parsed_df = df
            break
        except UnicodeDecodeError:
            continue
        except pd.errors.EmptyDataError:
            raise TSVEmptyError(f"The TSV file '{filename}' is empty or has no readable content.")
        except pd.errors.ParserError as e:
            raise TSVParsingError(f"Unable to parse TSV structure in '{filename}': {str(e)}")
        except Exception as e:
            if isinstance(e, (TSVExplorerError, CSVExplorerError)):
                raise
            raise TSVParsingError(f"Error parsing TSV '{filename}': {str(e)}")

    if parsed_df is None:
        raise TSVParsingError(
            f"Failed to decode '{filename}' using supported encodings "
            f"({', '.join(candidate_encodings)})."
        )

    if successful_encoding in ["latin1", "cp1252", "iso-8859-1"]:
        warnings.append(
            f"File parsed using fallback encoding '{successful_encoding}'."
        )

    has_headers_only = len(parsed_df) == 0
    if has_headers_only:
        warnings.append("Dataset contains column headers but zero data rows.")

    original_cols = [str(c) for c in parsed_df.columns]
    metadata = LoadMetadata(
        filename=filename,
        file_size_bytes=len(raw_bytes),
        encoding_used=successful_encoding,
        warnings=warnings,
        has_headers_only=has_headers_only,
        original_column_names=original_cols,
    )
    parsed_df.attrs["load_metadata"] = metadata

    return LoadResult(df=parsed_df, metadata=metadata)
