"""Unit tests for Analytix TSV data loader."""

import io
import pytest
import pandas as pd

from src.tsv_loader import (
    TSVEmptyError,
    TSVParsingError,
    load_tsv_detailed,
)


def test_load_tsv_valid():
    """Verify loading valid TSV data with tab delimiter."""
    tsv_content = b"id\tname\tscore\tpassed\n1\tAlice\t98.5\tTrue\n2\tBob\t82.0\tTrue\n3\tCharlie\t54.0\tFalse\n"
    res = load_tsv_detailed(io.BytesIO(tsv_content))
    assert len(res.df) == 3
    assert list(res.df.columns) == ["id", "name", "score", "passed"]
    assert res.df["score"].iloc[0] == 98.5
    assert not res.metadata.has_headers_only


def test_load_tsv_empty_error():
    """Verify empty TSV raises TSVEmptyError."""
    with pytest.raises(TSVEmptyError):
        load_tsv_detailed(io.BytesIO(b""))


def test_load_tsv_whitespace_only():
    """Verify whitespace-only TSV raises TSVEmptyError."""
    with pytest.raises(TSVEmptyError):
        load_tsv_detailed(io.BytesIO(b"   \t\n  \t\n"))


def test_load_tsv_duplicate_headers():
    """Verify duplicate headers in TSV are safely renamed with warnings."""
    tsv_content = b"col\tcol\tval\n1\t2\t3\n"
    res = load_tsv_detailed(io.BytesIO(tsv_content))
    assert len(res.df.columns) == 3
    assert len(res.metadata.warnings) > 0
