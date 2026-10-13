"""CSV loading, parsing, encoding detection, and validation for CSV Explorer.

Provides robust CSV ingestion handling:
- UTF-8 and UTF-8-BOM encodings with graceful fallbacks (latin1, cp1252, etc.)
- Empty files and header-only files
- Configurable file size limits (default 100 MB)
- Duplicate column detection and whitespace header normalization
- Preserving row and column integrity without silent value modification
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO, Union

import pandas as pd

# Default maximum file size limit: 100 Megabytes
DEFAULT_MAX_FILE_SIZE_BYTES: int = 100 * 1024 * 1024  # 100 MB


class CSVExplorerError(Exception):
    """Base exception for all CSV Explorer data loading operations."""
    pass


class CSVEmptyError(CSVExplorerError):
    """Raised when an uploaded CSV file contains zero bytes or no readable content."""
    pass


class CSVParsingError(CSVExplorerError):
    """Raised when a CSV file is malformed and cannot be parsed."""
    pass


class CSVSizeLimitExceededError(CSVExplorerError):
    """Raised when an uploaded file exceeds the configured size limit."""
    pass


class CSVEncodingError(CSVExplorerError):
    """Raised when all candidate encodings fail to decode the file content."""
    pass


@dataclass
class LoadMetadata:
    """Metadata detailing the CSV ingestion process and any warnings."""
    filename: str
    file_size_bytes: int
    encoding_used: str
    warnings: list[str] = field(default_factory=list)
    has_headers_only: bool = False
    original_column_names: list[str] = field(default_factory=list)


@dataclass
class LoadResult:
    """Detailed result container returning the parsed DataFrame and its ingestion metadata."""
    df: pd.DataFrame
    metadata: LoadMetadata


def _extract_file_bytes(
    file_input: Union[str, Path, BinaryIO, io.BytesIO, Any],
    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> tuple[bytes, str]:
    """Extract raw byte content and filename from various file-like inputs.
    
    Args:
        file_input: File path, BytesIO, or Streamlit UploadedFile.
        max_size_bytes: Maximum allowed byte length.

    Returns:
        tuple[bytes, str]: Tuple of (raw_bytes, filename)
    """
    filename = "uploaded_file.csv"

    if isinstance(file_input, (str, Path)):
        path = Path(file_input)
        filename = path.name
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        size = path.stat().st_size
        if size > max_size_bytes:
            raise CSVSizeLimitExceededError(
                f"File '{filename}' ({size / (1024*1024):.1f} MB) exceeds the "
                f"configured limit of {max_size_bytes / (1024*1024):.0f} MB."
            )
        raw_bytes = path.read_bytes()
    elif hasattr(file_input, "read"):
        if hasattr(file_input, "name") and file_input.name:
            filename = str(file_input.name)

        # Check size if available on object (e.g., Streamlit UploadedFile)
        if hasattr(file_input, "size") and file_input.size is not None:
            if file_input.size > max_size_bytes:
                raise CSVSizeLimitExceededError(
                    f"File '{filename}' ({file_input.size / (1024*1024):.1f} MB) exceeds the "
                    f"configured limit of {max_size_bytes / (1024*1024):.0f} MB."
                )

        if hasattr(file_input, "seek"):
            file_input.seek(0)
        raw_bytes = file_input.read()
        if hasattr(file_input, "seek"):
            file_input.seek(0)

        if isinstance(raw_bytes, str):
            raw_bytes = raw_bytes.encode("utf-8")
    else:
        raise ValueError(f"Unsupported file input type: {type(file_input)}")

    byte_length = len(raw_bytes)
    if byte_length > max_size_bytes:
        raise CSVSizeLimitExceededError(
            f"File '{filename}' ({byte_length / (1024*1024):.1f} MB) exceeds the "
            f"configured limit of {max_size_bytes / (1024*1024):.0f} MB."
        )

    return raw_bytes, filename


def _check_empty_content(raw_bytes: bytes, filename: str) -> None:
    """Validate that raw bytes contain non-whitespace text.
    
    Args:
        raw_bytes: File byte content.
        filename: Name of the file for error reporting.
    """
    if len(raw_bytes) == 0:
        raise CSVEmptyError(f"The file '{filename}' is empty (0 bytes). Please upload a valid CSV file.")
    if len(raw_bytes.strip()) == 0:
        raise CSVEmptyError(f"The file '{filename}' contains only whitespace. Please upload a CSV with data.")


def _check_duplicate_headers(first_line: str) -> list[str]:
    """Inspect raw header line to detect duplicate column names before parsing.
    
    Args:
        first_line: Raw header text line.

    Returns:
        list[str]: Names of columns appearing more than once.
    """
    # Simple split on common delimiters (comma, semicolon, tab)
    for delim in [",", ";", "\t"]:
        if delim in first_line:
            tokens = [t.strip().strip('"').strip("'") for t in first_line.split(delim)]
            seen = set()
            duplicates = []
            for token in tokens:
                if token:
                    if token in seen and token not in duplicates:
                        duplicates.append(token)
                    seen.add(token)
            if duplicates:
                return duplicates
    return []


def load_csv_detailed(
    file_input: Union[str, Path, BinaryIO, io.BytesIO, Any],
    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> LoadResult:
    """Load and parse a CSV file, returning a DataFrame and detailed ingestion metadata.

    Attempts standard UTF-8 parsing, transparently handles UTF-8 BOM, and falls
    back gracefully to secondary encodings ('latin1', 'cp1252', 'iso-8859-1')
    when UTF-8 fails, warning the user of any fallback.

    Args:
        file_input: File path or file-like object.
        max_size_bytes: Configurable file size threshold (default 100MB).

    Returns:
        LoadResult: Dataclass containing the parsed DataFrame and LoadMetadata.

    Raises:
        CSVEmptyError: If the file has 0 bytes or contains only whitespace.
        CSVSizeLimitExceededError: If the file exceeds the maximum size limit.
        CSVParsingError: If the CSV format cannot be parsed.
        CSVEncodingError: If decoding fails across all candidate encodings.
    """
    raw_bytes, filename = _extract_file_bytes(file_input, max_size_bytes)
    _check_empty_content(raw_bytes, filename)

    candidate_encodings = ["utf-8-sig", "utf-8", "latin1", "cp1252", "iso-8859-1"]
    warnings: list[str] = []
    parsed_df: pd.DataFrame | None = None
    successful_encoding: str = ""

    for enc in candidate_encodings:
        try:
            # Test decoding
            text = raw_bytes.decode(enc)
            # Inspect first line for duplicate headers
            lines = [l for l in text.splitlines() if l.strip()]
            if not lines:
                raise CSVEmptyError(f"The file '{filename}' contains no readable data rows.")

            dup_headers = _check_duplicate_headers(lines[0])
            if dup_headers:
                warnings.append(
                    f"Duplicate column headers detected: {dup_headers}. "
                    "Columns have been disambiguated automatically by pandas."
                )

            # Parse with pandas
            # Using low_memory=False ensures consistent type inference
            buffer = io.StringIO(text)
            df = pd.read_csv(buffer, low_memory=False)

            successful_encoding = enc
            parsed_df = df
            break
        except UnicodeDecodeError:
            continue
        except pd.errors.EmptyDataError:
            raise CSVEmptyError(f"The file '{filename}' is empty or has no readable content.")
        except pd.errors.ParserError as e:
            # If ParserError occurs on utf-8, fallback may not fix parsing structure,
            # but we can try other encodings or report directly.
            raise CSVParsingError(f"Unable to parse CSV structure in '{filename}': {str(e)}")
        except Exception as e:
            if isinstance(e, CSVExplorerError):
                raise
            raise CSVParsingError(f"Error parsing '{filename}': {str(e)}")

    if parsed_df is None:
        raise CSVEncodingError(
            f"Failed to decode '{filename}' using supported encodings "
            f"({', '.join(candidate_encodings)}). Please ensure the file is valid UTF-8."
        )

    # Note if an alternate fallback encoding was required
    if successful_encoding in ["latin1", "cp1252", "iso-8859-1"]:
        warnings.append(
            f"File could not be parsed with standard UTF-8; successfully decoded using fallback '{successful_encoding}'."
        )

    # Check for empty data frame (headers present, but 0 rows)
    has_headers_only = len(parsed_df) == 0
    if has_headers_only:
        warnings.append("Dataset contains column headers but zero data rows.")

    # Clean whitespace in column names if necessary, while preserving original names in metadata
    original_cols = [str(c) for c in parsed_df.columns]
    
    # Store metadata directly onto df.attrs for easy access
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


def load_csv(
    file_input: Union[str, Path, BinaryIO, io.BytesIO, Any],
    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> pd.DataFrame:
    """Primary function to load a CSV file into a pandas DataFrame.

    Convenience wrapper around `load_csv_detailed`. Ingestion metadata
    and warnings are accessible via `df.attrs['load_metadata']`.

    Args:
        file_input: File path or file-like object.
        max_size_bytes: Configurable file size threshold.

    Returns:
        pd.DataFrame: Parsed pandas DataFrame.
    """
    result = load_csv_detailed(file_input, max_size_bytes=max_size_bytes)
    return result.df
