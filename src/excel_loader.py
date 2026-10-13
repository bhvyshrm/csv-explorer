"""Excel workbook (.xlsx, .xls) inspection, multi-sheet discovery, and data ingestion for Analytix.

Provides:
- Workbook metadata inspection (sheet names, dimensions, emptiness detection)
- Modern .xlsx parsing via openpyxl (with data_only=True for evaluated formula results)
- Legacy .xls parsing via xlrd where applicable
- Preservation of dates, numerics, and boolean data types
- Controlled error handling for corrupted files, empty sheets, and size limits
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO, Optional, Union

import pandas as pd

from src.data_loader import (
    DEFAULT_MAX_FILE_SIZE_BYTES,
    CSVExplorerError,
    CSVSizeLimitExceededError,
    LoadMetadata,
    LoadResult,
    _extract_file_bytes,
)


class ExcelExplorerError(CSVExplorerError):
    """Base exception for Excel workbook operations in Analytix."""
    pass


class ExcelUnsupportedFormatError(ExcelExplorerError):
    """Raised when an uploaded file is not a supported Excel workbook (.xlsx, .xls)."""
    pass


class ExcelCorruptedError(ExcelExplorerError):
    """Raised when an Excel file cannot be opened due to corruption or malformed structure."""
    pass


class ExcelEmptyWorkbookError(ExcelExplorerError):
    """Raised when an Excel workbook has zero sheets or zero data."""
    pass


class ExcelEmptySheetError(ExcelExplorerError):
    """Raised when the selected worksheet contains no data rows."""
    pass


class ExcelSheetNotFoundError(ExcelExplorerError):
    """Raised when the requested worksheet name does not exist in the workbook."""
    pass


@dataclass
class SheetMetadata:
    """Metadata detailing an individual worksheet within an Excel workbook."""
    name: str
    row_count: int
    col_count: int
    is_empty: bool
    sample_headers: list[str] = field(default_factory=list)


@dataclass
class WorkbookMetadata:
    """Metadata describing the overall Excel workbook and its available sheets."""
    filename: str
    file_size_bytes: int
    file_format: str  # '.xlsx' or '.xls'
    sheet_names: list[str]
    sheets: list[SheetMetadata]
    total_sheets: int


def _detect_excel_format(filename: str) -> str:
    """Determine whether the file extension corresponds to a valid Excel workbook.

    Args:
        filename: Name of the file.

    Returns:
        str: '.xlsx' or '.xls'

    Raises:
        ExcelUnsupportedFormatError: If the extension is not .xlsx or .xls.
    """
    fn_lower = filename.lower()
    if fn_lower.endswith(".xlsx") or fn_lower.endswith(".xlsm"):
        return ".xlsx"
    if fn_lower.endswith(".xls"):
        return ".xls"
    raise ExcelUnsupportedFormatError(
        f"File '{filename}' is not a supported Excel format. "
        "Analytix supports modern (.xlsx) and legacy (.xls) Excel workbooks."
    )


def inspect_excel_workbook(
    file_input: Union[str, Path, BinaryIO, io.BytesIO, Any],
    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> WorkbookMetadata:
    """Inspect an Excel workbook and discover its worksheets and sheet-level dimensions.

    Args:
        file_input: File path, BytesIO, or Streamlit UploadedFile.
        max_size_bytes: Maximum allowed byte length.

    Returns:
        WorkbookMetadata: Summary of sheets, row/column counts, and sample headers.

    Raises:
        ExcelUnsupportedFormatError: If the file is not .xlsx or .xls.
        ExcelCorruptedError: If workbook structure cannot be parsed.
        ExcelEmptyWorkbookError: If workbook contains no sheets.
    """
    raw_bytes, filename = _extract_file_bytes(file_input, max_size_bytes)
    file_format = _detect_excel_format(filename)

    buffer = io.BytesIO(raw_bytes)
    sheets_info: list[SheetMetadata] = []

    try:
        if file_format == ".xlsx":
            import openpyxl

            try:
                # read_only=True offers high-performance dimension inspection
                wb = openpyxl.load_workbook(buffer, read_only=True, data_only=True)
                sheet_names = wb.sheetnames
            except Exception as e:
                raise ExcelCorruptedError(f"Unable to read Excel workbook '{filename}': {str(e)}")

            if not sheet_names:
                raise ExcelEmptyWorkbookError(f"Workbook '{filename}' contains no worksheets.")

            for s_name in sheet_names:
                ws = wb[s_name]
                # In read-only mode, max_row and max_column give sheet boundaries
                r_count = ws.max_row or 0
                c_count = ws.max_column or 0
                
                # Fetch first row for sample headers
                headers = []
                is_empty = (r_count == 0 or c_count == 0)
                if not is_empty:
                    first_row = next(ws.iter_rows(max_row=1, values_only=True), None)
                    if first_row:
                        headers = [str(cell) for cell in first_row if cell is not None]
                        # If first row has zero non-null cells, consider empty
                        if not headers:
                            is_empty = True

                sheets_info.append(
                    SheetMetadata(
                        name=s_name,
                        row_count=r_count,
                        col_count=c_count,
                        is_empty=is_empty,
                        sample_headers=headers[:8],
                    )
                )
            wb.close()

        else:  # .xls legacy format
            import xlrd

            try:
                wb = xlrd.open_workbook(file_contents=raw_bytes)
                sheet_names = wb.sheet_names()
            except Exception as e:
                raise ExcelCorruptedError(f"Unable to read legacy .xls workbook '{filename}': {str(e)}")

            if not sheet_names:
                raise ExcelEmptyWorkbookError(f"Workbook '{filename}' contains no worksheets.")

            for s_name in sheet_names:
                sh = wb.sheet_by_name(s_name)
                r_count = sh.nrows
                c_count = sh.ncols
                headers = []
                is_empty = (r_count == 0 or c_count == 0)
                if not is_empty:
                    first_row_vals = sh.row_values(0)
                    headers = [str(v) for v in first_row_vals if v not in ("", None)]
                    if not headers:
                        is_empty = True

                sheets_info.append(
                    SheetMetadata(
                        name=s_name,
                        row_count=r_count,
                        col_count=c_count,
                        is_empty=is_empty,
                        sample_headers=headers[:8],
                    )
                )

    except ExcelExplorerError:
        raise
    except Exception as e:
        raise ExcelCorruptedError(f"Error inspecting Excel workbook '{filename}': {str(e)}")

    return WorkbookMetadata(
        filename=filename,
        file_size_bytes=len(raw_bytes),
        file_format=file_format,
        sheet_names=[s.name for s in sheets_info],
        sheets=sheets_info,
        total_sheets=len(sheets_info),
    )


def load_excel_sheet(
    file_input: Union[str, Path, BinaryIO, io.BytesIO, Any],
    sheet_name: Optional[str] = None,
    header_row: Optional[int] = 0,
    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> LoadResult:
    """Load an individual worksheet from an Excel workbook into a pandas DataFrame.

    Preserves dates, numerics, and categorical strings, handles formula outputs,
    and returns comprehensive LoadResult metadata for integration into Analytix.

    Args:
        file_input: File path, BytesIO, or Streamlit UploadedFile.
        sheet_name: Name of the worksheet to load. If None, loads the first sheet.
        header_row: Zero-indexed row number containing column headers (default 0).
                    Pass None if the sheet has no header row.
        max_size_bytes: File size cap.

    Returns:
        LoadResult: Parsed pandas DataFrame and associated ingestion metadata.

    Raises:
        ExcelUnsupportedFormatError: If file extension is unsupported.
        ExcelCorruptedError: If file is corrupted or unreadable.
        ExcelSheetNotFoundError: If specified sheet_name does not exist.
        ExcelEmptySheetError: If the selected sheet contains no readable rows.
    """
    raw_bytes, filename = _extract_file_bytes(file_input, max_size_bytes)
    file_format = _detect_excel_format(filename)

    buffer = io.BytesIO(raw_bytes)
    engine = "openpyxl" if file_format == ".xlsx" else "xlrd"

    # Inspect sheet names first to validate requested sheet
    try:
        excel_file = pd.ExcelFile(buffer, engine=engine)
        available_sheets = excel_file.sheet_names
    except Exception as e:
        raise ExcelCorruptedError(f"Corrupted or invalid Excel file '{filename}': {str(e)}")

    if not available_sheets:
        raise ExcelEmptyWorkbookError(f"Workbook '{filename}' contains no worksheets.")

    target_sheet = sheet_name if sheet_name is not None else available_sheets[0]
    if target_sheet not in available_sheets:
        raise ExcelSheetNotFoundError(
            f"Worksheet '{target_sheet}' not found in workbook '{filename}'. "
            f"Available worksheets: {available_sheets}"
        )

    warnings: list[str] = []

    # Read selected sheet
    try:
        buffer.seek(0)
        df = pd.read_excel(
            buffer,
            sheet_name=target_sheet,
            header=header_row,
            engine=engine,
        )
    except Exception as e:
        raise ExcelCorruptedError(f"Failed to read worksheet '{target_sheet}' from '{filename}': {str(e)}")

    # Check for empty sheet
    if df.empty and len(df.columns) == 0:
        raise ExcelEmptySheetError(
            f"Worksheet '{target_sheet}' in '{filename}' is empty (0 rows and 0 columns)."
        )

    has_headers_only = len(df) == 0
    if has_headers_only:
        warnings.append(f"Worksheet '{target_sheet}' contains headers but zero data rows.")

    # Check for duplicate headers
    seen_cols = set()
    dup_cols = []
    for c in df.columns:
        col_str = str(c)
        if col_str in seen_cols and col_str not in dup_cols:
            dup_cols.append(col_str)
        seen_cols.add(col_str)

    if dup_cols:
        warnings.append(
            f"Duplicate column headers detected in '{target_sheet}': {dup_cols}. "
            "Disambiguated automatically by pandas."
        )

    # Note if formulas or date columns were detected
    date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
    if date_cols:
        warnings.append(f"Detected {len(date_cols)} datetime column(s): {date_cols}.")

    metadata = LoadMetadata(
        filename=filename,
        file_size_bytes=len(raw_bytes),
        encoding_used="Excel Binary (" + file_format + ")",
        warnings=warnings,
        has_headers_only=has_headers_only,
        original_column_names=[str(c) for c in df.columns],
    )

    # Attach extended attributes for Analytix Excel workflow
    df.attrs["load_metadata"] = metadata
    df.attrs["source_format"] = f"Excel ({file_format})"
    df.attrs["active_worksheet"] = target_sheet
    df.attrs["available_worksheets"] = available_sheets

    return LoadResult(df=df, metadata=metadata)
