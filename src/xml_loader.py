"""Safe XML data loader and converter for Analytix.

Provides secure tabular ingestion of structured XML documents:
- Hardened against XML External Entity (XXE) and entity expansion attacks (Billion Laughs)
- Automatic discovery of repeating record elements under the root or container nodes
- Extracts both element text content and attributes into standardized tabular columns
- Meaningful error diagnostics for malformed or empty XML files
"""

from __future__ import annotations

import io
import re
import xml.etree.ElementTree as ET
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


class XMLExplorerError(CSVExplorerError):
    """Base exception for XML loading operations."""
    pass


class XMLEmptyError(XMLExplorerError):
    """Raised when an XML file is empty."""
    pass


class XMLParsingError(XMLExplorerError):
    """Raised when an XML document is malformed or violates security policies."""
    pass


# Security guard: disallow DOCTYPE with entity declarations to block XXE & billion laughs attacks
_DISALLOWED_XML_PATTERNS = [
    re.compile(rb"<!DOCTYPE[^>]*\[", re.IGNORECASE),
    re.compile(rb"<!ENTITY", re.IGNORECASE),
    re.compile(rb"SYSTEM\s+[\"']", re.IGNORECASE),
]


def load_xml_detailed(
    file_input: Union[str, Path, BinaryIO, io.BytesIO, Any],
    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> LoadResult:
    """Safely parse and convert structured XML into a tabular DataFrame.

    Args:
        file_input: File path, BytesIO, or file-like object.
        max_size_bytes: Maximum allowed file size in bytes.

    Returns:
        LoadResult: Parsed DataFrame and ingestion metadata.
    """
    raw_bytes, filename = _extract_file_bytes(file_input, max_size_bytes)

    if len(raw_bytes) == 0 or not raw_bytes.strip():
        raise XMLEmptyError(f"The XML file '{filename}' is empty (0 bytes).")

    # Enforce safe parsing policy
    for pattern in _DISALLOWED_XML_PATTERNS:
        if pattern.search(raw_bytes):
            raise XMLParsingError(
                f"Security check failed for '{filename}': custom DOCTYPE/ENTITY declarations "
                "are disabled to prevent XML External Entity (XXE) vulnerabilities."
            )

    try:
        root = ET.fromstring(raw_bytes)
    except ET.ParseError as exc:
        raise XMLParsingError(f"Malformed XML syntax in '{filename}': {str(exc)}") from exc
    except Exception as exc:
        raise XMLParsingError(f"Failed to parse XML in '{filename}': {str(exc)}") from exc

    # Identify repeating record elements
    children = list(root)
    if not children:
        # Check if root has text or attributes
        if root.attrib:
            df = pd.DataFrame([root.attrib])
            warnings = ["Single XML root element with attributes parsed as 1-row table."]
        else:
            raise XMLEmptyError(f"The XML file '{filename}' contains an empty root element with no records.")
    else:
        # Group children by tag to find the most common repeating node
        tag_counts: dict[str, int] = {}
        for c in children:
            tag_counts[c.tag] = tag_counts.get(c.tag, 0) + 1

        primary_tag, count = max(tag_counts.items(), key=lambda item: item[1])

        # If primary tag has its own repeating children, e.g. <catalog><products><product>...</products></catalog>
        records_to_parse = [c for c in children if c.tag == primary_tag]
        if count == 1 and len(records_to_parse[0]) > 1:
            nested_children = list(records_to_parse[0])
            nested_counts: dict[str, int] = {}
            for nc in nested_children:
                nested_counts[nc.tag] = nested_counts.get(nc.tag, 0) + 1
            if nested_counts:
                nested_primary = max(nested_counts.items(), key=lambda item: item[1])[0]
                records_to_parse = [nc for nc in nested_children if nc.tag == nested_primary]

        rows: list[dict[str, Any]] = []
        for elem in records_to_parse:
            row: dict[str, Any] = {}
            # Add element attributes prefixed if needed
            for k, v in elem.attrib.items():
                row[f"@{k}"] = v

            # Add child elements
            for sub in elem:
                sub_tag = sub.tag.split("}")[-1] if "}" in sub.tag else sub.tag
                row[sub_tag] = (sub.text or "").strip() if sub.text else None

            # If element has direct text and no children
            if not len(elem) and elem.text and elem.text.strip():
                row["text"] = elem.text.strip()

            if row:
                rows.append(row)

        if not rows:
            raise XMLEmptyError(f"The XML file '{filename}' contains elements but no extractable data rows.")

        df = pd.DataFrame(rows)
        warnings = [f"Extracted {len(df):,} tabular rows from XML element '<{primary_tag}>'."]

    original_cols = [str(c) for c in df.columns]
    metadata = LoadMetadata(
        filename=filename,
        file_size_bytes=len(raw_bytes),
        encoding_used="utf-8/xml",
        warnings=warnings,
        has_headers_only=len(df) == 0,
        original_column_names=original_cols,
    )
    df.attrs["load_metadata"] = metadata

    return LoadResult(df=df, metadata=metadata)
