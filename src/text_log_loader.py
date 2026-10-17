"""Text and Log file analyzer and parser for Analytix.

Provides specialized handling for:
- Plain text (.txt) and log files (.log)
- Line counts, blank lines, token counts, character statistics
- Structured log detection (ISO timestamp, severity levels INFO/WARN/ERROR/DEBUG, or web access logs)
- Clean line-by-line tabular representation for unstructured text without fabricating false columns
"""

from __future__ import annotations

import io
import re
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


class TextLogExplorerError(CSVExplorerError):
    """Base exception for text and log operations."""
    pass


class TextLogEmptyError(TextLogExplorerError):
    """Raised when a text or log file is empty."""
    pass


# Standard log patterns
# 1. ISO/Standard timestamp + Level: 2026-10-17 10:15:30 [INFO] User logged in
LOG_PATTERN_TIMESTAMP_LEVEL = re.compile(
    r"^\[?(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\]?\s+"
    r"(?:\[(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL)\]|(?P<level_alt>DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL):?)\s+"
    r"(?P<message>.*)$",
    re.IGNORECASE,
)

# 2. Apache/Nginx Combined Log: 127.0.0.1 - - [17/Oct/2026:10:15:30 +0000] "GET /api HTTP/1.1" 200 452
WEB_LOG_PATTERN = re.compile(
    r'^(?P<client_ip>\S+)\s+\S+\s+\S+\s+\[(?P<timestamp>[^\]]+)\]\s+"(?P<method>\S+)\s+(?P<path>\S+)\s+(?P<protocol>[^"]+)"\s+(?P<status_code>\d{3})\s+(?P<response_size>\S+)',
)


def load_text_or_log_detailed(
    file_input: Union[str, Path, BinaryIO, io.BytesIO, Any],
    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> LoadResult:
    """Analyze and ingest text or log files into a normalized DataFrame.

    If reliable log structure is detected across lines, extracts structured fields
    (timestamp, level, message, or web log metrics). Otherwise, provides an honest
    line-by-line inspection structure with text metrics.

    Args:
        file_input: File path, BytesIO, or file-like object.
        max_size_bytes: Maximum allowed file size in bytes.

    Returns:
        LoadResult: Parsed DataFrame and ingestion metadata.
    """
    raw_bytes, filename = _extract_file_bytes(file_input, max_size_bytes)

    if len(raw_bytes) == 0:
        raise TextLogEmptyError(f"The file '{filename}' is empty (0 bytes).")

    try:
        text = raw_bytes.decode("utf-8-sig")
        encoding_used = "utf-8"
    except UnicodeDecodeError:
        text = raw_bytes.decode("latin1", errors="replace")
        encoding_used = "latin1"

    lines = text.splitlines()
    if not lines or (len(lines) == 1 and not lines[0].strip()):
        raise TextLogEmptyError(f"The file '{filename}' contains only whitespace.")

    total_lines = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    non_blank_lines = total_lines - blank_lines
    total_characters = len(text)
    total_words = sum(len(line.split()) for line in lines)

    warnings: list[str] = [
        f"File stats: {total_lines:,} lines ({blank_lines:,} blank), {total_words:,} words, {total_characters:,} characters."
    ]

    # Attempt structured log matching
    matched_timestamp_logs: list[dict[str, Any]] = []
    matched_web_logs: list[dict[str, Any]] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        m_log = LOG_PATTERN_TIMESTAMP_LEVEL.match(stripped)
        if m_log:
            level = m_log.group("level") or m_log.group("level_alt") or "INFO"
            matched_timestamp_logs.append(
                {
                    "timestamp": m_log.group("timestamp"),
                    "level": level.upper(),
                    "message": m_log.group("message"),
                }
            )
            continue

        m_web = WEB_LOG_PATTERN.match(stripped)
        if m_web:
            size_val = m_web.group("response_size")
            matched_web_logs.append(
                {
                    "client_ip": m_web.group("client_ip"),
                    "timestamp": m_web.group("timestamp"),
                    "method": m_web.group("method"),
                    "path": m_web.group("path"),
                    "status_code": int(m_web.group("status_code")),
                    "response_size_bytes": int(size_val) if size_val.isdigit() else 0,
                }
            )

    # Determine if structured logs represent significant portion of non-blank lines (>= 60%)
    if non_blank_lines > 0 and len(matched_timestamp_logs) / non_blank_lines >= 0.6:
        df = pd.DataFrame(matched_timestamp_logs)
        warnings.append(
            f"Structured log format recognized: parsed {len(matched_timestamp_logs)} log events with timestamps and severity levels."
        )
    elif non_blank_lines > 0 and len(matched_web_logs) / non_blank_lines >= 0.6:
        df = pd.DataFrame(matched_web_logs)
        warnings.append(
            f"Standard web server access log format recognized: parsed {len(matched_web_logs)} HTTP request events."
        )
    else:
        # Unstructured text: line-by-line inspection table
        df = pd.DataFrame(
            [
                {
                    "line_number": idx,
                    "character_count": len(line),
                    "word_count": len(line.split()),
                    "is_blank": not bool(line.strip()),
                    "text_content": line[:300],  # preview up to 300 chars
                }
                for idx, line in enumerate(lines, start=1)
            ]
        )
        warnings.append(
            "Text format loaded as line-by-line inspection table with character and word statistics."
        )

    original_cols = [str(c) for c in df.columns]
    metadata = LoadMetadata(
        filename=filename,
        file_size_bytes=len(raw_bytes),
        encoding_used=encoding_used,
        warnings=warnings,
        has_headers_only=False,
        original_column_names=original_cols,
    )
    df.attrs["load_metadata"] = metadata

    return LoadResult(df=df, metadata=metadata)
