"""Centralized file format registry and multi-format dispatcher for Analytix.

Provides modular dispatching across all supported tabular and semi-structured formats:
- CSV (.csv)
- Excel (.xlsx, .xls)
- TSV (.tsv, .tab)
- JSON (.json)
- NDJSON / JSONL (.ndjson, .jsonl)
- Parquet (.parquet)
- Text and Logs (.txt, .log)
- XML (.xml)
- Database Explorer (Planned)
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Optional, Union

import pandas as pd

from src.data_loader import (
    DEFAULT_MAX_FILE_SIZE_BYTES,
    CSVExplorerError,
    LoadMetadata,
    LoadResult,
    load_csv_detailed,
)
from src.excel_loader import (
    WorkbookMetadata,
    inspect_excel_workbook,
    load_excel_sheet,
)
from src.json_loader import load_json_detailed, load_ndjson_detailed
from src.parquet_loader import load_parquet_detailed
from src.text_log_loader import load_text_or_log_detailed
from src.tsv_loader import load_tsv_detailed
from src.xml_loader import load_xml_detailed


class UnsupportedFormatError(CSVExplorerError):
    """Raised when an uploaded file extension or content is unsupported."""
    pass


@dataclass
class FormatDescriptor:
    """Descriptor defining a format capability, status, and supported extensions."""
    id: str
    name: str
    description: str
    extensions: list[str]
    is_available: bool
    status_label: str  # "Available" or "Coming soon"
    category: str


SUPPORTED_FORMATS: list[FormatDescriptor] = [
    FormatDescriptor(
        id="csv",
        name="CSV Explorer",
        description="Inspect standard comma-separated datasets with automatic delimiter detection and encoding fallbacks.",
        extensions=[".csv"],
        is_available=True,
        status_label="Available",
        category="Tabular",
    ),
    FormatDescriptor(
        id="excel",
        name="Excel Explorer",
        description="Multi-sheet Excel workbook inspection, worksheet discovery, formula evaluation, and sheet switching.",
        extensions=[".xlsx", ".xls"],
        is_available=True,
        status_label="Available",
        category="Spreadsheet",
    ),
    FormatDescriptor(
        id="json",
        name="JSON Explorer",
        description="Parse JSON arrays, records, and newline-delimited JSON (NDJSON/JSONL) with automated nested flattening.",
        extensions=[".json", ".jsonl", ".ndjson"],
        is_available=True,
        status_label="Available",
        category="Hierarchical",
    ),
    FormatDescriptor(
        id="parquet",
        name="Parquet Explorer",
        description="High-performance Apache Parquet columnar reader with native schema inspection and type preservation.",
        extensions=[".parquet"],
        is_available=True,
        status_label="Available",
        category="Columnar",
    ),
    FormatDescriptor(
        id="text-log",
        name="Text & Log Explorer",
        description="Analyze log files and text documents with timestamp extraction, log level parsing, and line statistics.",
        extensions=[".txt", ".log"],
        is_available=True,
        status_label="Available",
        category="Unstructured",
    ),
    FormatDescriptor(
        id="tsv",
        name="TSV Explorer",
        description="Explore tab-separated files with dedicated delimiter handling and encoding fallbacks.",
        extensions=[".tsv", ".tab"],
        is_available=True,
        status_label="Available",
        category="Tabular",
    ),
    FormatDescriptor(
        id="xml",
        name="XML Explorer",
        description="Safe XML document parser converting repeating child records and attributes into tabular datasets.",
        extensions=[".xml"],
        is_available=True,
        status_label="Available",
        category="Structured",
    ),
    FormatDescriptor(
        id="database",
        name="Database Explorer",
        description="Connect directly to SQL databases (PostgreSQL, MySQL, SQLite) to query and analyze live tables.",
        extensions=[],
        is_available=False,
        status_label="Coming soon",
        category="Database",
    ),
]


@dataclass
class UniversalLoadResult:
    """Unified container returning normalized DataFrame, format information, and metadata."""
    df: pd.DataFrame
    format_type: str
    filename: str
    metadata: LoadMetadata
    active_worksheet: Optional[str] = None
    workbook_meta: Optional[WorkbookMetadata] = None


def detect_and_load_file(
    file_input: Union[str, Path, BinaryIO, io.BytesIO, Any],
    filename: Optional[str] = None,
    sheet_name: Optional[str] = None,
    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> UniversalLoadResult:
    """Detect file format from extension and dispatch to the appropriate specialized loader.

    Args:
        file_input: File path, BytesIO, or file-like object.
        filename: Optional explicit filename (inferred from input if omitted).
        sheet_name: Optional worksheet name for Excel files.
        max_size_bytes: Maximum allowed file size in bytes.

    Returns:
        UniversalLoadResult: Standardized container with DataFrame and metadata.
    """
    detected_name = filename or getattr(file_input, "name", None) or "uploaded_file"
    ext = Path(detected_name).suffix.lower()

    if ext == ".csv":
        res = load_csv_detailed(file_input, max_size_bytes=max_size_bytes)
        return UniversalLoadResult(
            df=res.df,
            format_type="CSV",
            filename=res.metadata.filename,
            metadata=res.metadata,
        )

    if ext in (".xlsx", ".xls"):
        # Excel inspection and sheet loading
        wb_meta = inspect_excel_workbook(file_input, max_size_bytes=max_size_bytes)
        target_sheet = sheet_name or wb_meta.sheet_names[0]
        # Rewind buffer if seekable
        if hasattr(file_input, "seek"):
            file_input.seek(0)
        res = load_excel_sheet(file_input, sheet_name=target_sheet, max_size_bytes=max_size_bytes)
        format_label = f"Excel ({wb_meta.file_format})"
        return UniversalLoadResult(
            df=res.df,
            format_type=format_label,
            filename=wb_meta.filename,
            metadata=res.metadata,
            active_worksheet=target_sheet,
            workbook_meta=wb_meta,
        )

    if ext in (".tsv", ".tab"):
        res = load_tsv_detailed(file_input, max_size_bytes=max_size_bytes)
        return UniversalLoadResult(
            df=res.df,
            format_type="TSV",
            filename=res.metadata.filename,
            metadata=res.metadata,
        )

    if ext == ".json":
        res = load_json_detailed(file_input, max_size_bytes=max_size_bytes)
        return UniversalLoadResult(
            df=res.df,
            format_type="JSON",
            filename=res.metadata.filename,
            metadata=res.metadata,
        )

    if ext in (".ndjson", ".jsonl"):
        res = load_ndjson_detailed(file_input, max_size_bytes=max_size_bytes)
        return UniversalLoadResult(
            df=res.df,
            format_type="NDJSON",
            filename=res.metadata.filename,
            metadata=res.metadata,
        )

    if ext == ".parquet":
        res = load_parquet_detailed(file_input, max_size_bytes=max_size_bytes)
        return UniversalLoadResult(
            df=res.df,
            format_type="Parquet",
            filename=res.metadata.filename,
            metadata=res.metadata,
        )

    if ext in (".txt", ".log"):
        res = load_text_or_log_detailed(file_input, max_size_bytes=max_size_bytes)
        format_type = "Log" if ext == ".log" else "Text"
        return UniversalLoadResult(
            df=res.df,
            format_type=format_type,
            filename=res.metadata.filename,
            metadata=res.metadata,
        )

    if ext == ".xml":
        res = load_xml_detailed(file_input, max_size_bytes=max_size_bytes)
        return UniversalLoadResult(
            df=res.df,
            format_type="XML",
            filename=res.metadata.filename,
            metadata=res.metadata,
        )

    supported_exts = [".csv", ".xlsx", ".xls", ".tsv", ".json", ".ndjson", ".jsonl", ".parquet", ".txt", ".log", ".xml"]
    raise UnsupportedFormatError(
        f"Unsupported file format '{ext}'. Analytix supports: {', '.join(supported_exts)}."
    )
