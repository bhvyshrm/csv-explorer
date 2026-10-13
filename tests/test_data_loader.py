"""Unit tests for src/data_loader.py."""

import io
from pathlib import Path
import pytest
import pandas as pd

from src.data_loader import (
    load_csv,
    load_csv_detailed,
    CSVEmptyError,
    CSVParsingError,
    CSVSizeLimitExceededError,
)


def test_valid_csv_loads_successfully():
    csv_data = "name,age,salary\nAlice,30,70000\nBob,25,50000\nCharlie,35,80000\n"
    bio = io.BytesIO(csv_data.encode("utf-8"))
    bio.name = "employees.csv"

    df = load_csv(bio)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert list(df.columns) == ["name", "age", "salary"]
    assert df["salary"].iloc[0] == 70000
    assert "load_metadata" in df.attrs
    assert df.attrs["load_metadata"].filename == "employees.csv"


def test_empty_file_raises_empty_error():
    empty_bio = io.BytesIO(b"")
    empty_bio.name = "empty.csv"
    with pytest.raises(CSVEmptyError):
        load_csv(empty_bio)


def test_whitespace_only_file_raises_empty_error():
    ws_bio = io.BytesIO(b"   \n   \t  \n  ")
    ws_bio.name = "blank.csv"
    with pytest.raises(CSVEmptyError):
        load_csv(ws_bio)


def test_headers_only_csv():
    headers_bio = io.BytesIO(b"col_a,col_b,col_c\n")
    headers_bio.name = "headers_only.csv"
    res = load_csv_detailed(headers_bio)
    assert len(res.df) == 0
    assert list(res.df.columns) == ["col_a", "col_b", "col_c"]
    assert res.metadata.has_headers_only is True
    assert any("headers but zero data rows" in w for w in res.metadata.warnings)


def test_utf8_bom_handled_transparently():
    # Byte Order Mark for UTF-8: \xef\xbb\xbf
    bom_content = b"\xef\xbb\xbfid,score\n1,95\n2,88\n"
    bio = io.BytesIO(bom_content)
    bio.name = "bom_data.csv"
    df = load_csv(bio)
    assert len(df) == 2
    # Ensure BOM did not get prepended to the first column name
    assert "id" in df.columns
    assert "\ufeffid" not in df.columns


def test_fallback_encoding_latin1():
    # Character 'é' in latin1 is byte 0xe9, which is invalid utf-8
    latin1_bytes = "nom,ville\nRené,Montréal\n".encode("latin1")
    bio = io.BytesIO(latin1_bytes)
    bio.name = "french.csv"
    res = load_csv_detailed(bio)
    assert len(res.df) == 1
    assert res.df["nom"].iloc[0] == "René"
    assert any("fallback" in w.lower() for w in res.metadata.warnings)


def test_duplicate_column_headers_detected():
    dup_csv = b"item,price,item\nBook,12,Notebook\n"
    bio = io.BytesIO(dup_csv)
    bio.name = "dup.csv"
    res = load_csv_detailed(bio)
    assert len(res.df) == 1
    assert any("Duplicate column headers" in w for w in res.metadata.warnings)


def test_file_size_limit_exceeded():
    large_content = b"a,b\n1,2\n" * 100
    bio = io.BytesIO(large_content)
    bio.name = "capped.csv"
    # Set limit smaller than content
    with pytest.raises(CSVSizeLimitExceededError):
        load_csv(bio, max_size_bytes=50)


def test_missing_values_preserved():
    csv_data = "col1,col2,col3\n1,,foo\n,4.5,\n"
    bio = io.BytesIO(csv_data.encode("utf-8"))
    df = load_csv(bio)
    assert len(df) == 2
    assert pd.isna(df.loc[0, "col2"])
    assert pd.isna(df.loc[1, "col1"])
    assert pd.isna(df.loc[1, "col3"])


def test_numeric_values_parsed_appropriately():
    csv_data = "int_col,float_col,str_col\n42,3.14159,hello\n100,2.71828,world\n"
    bio = io.BytesIO(csv_data.encode("utf-8"))
    df = load_csv(bio)
    assert pd.api.types.is_integer_dtype(df["int_col"])
    assert pd.api.types.is_float_dtype(df["float_col"])
    assert pd.api.types.is_string_dtype(df["str_col"]) or pd.api.types.is_object_dtype(df["str_col"])


def test_load_sample_superstore_file():
    sample_path = Path("sample_data/sample_superstore_eda.csv")
    assert sample_path.exists()
    df = load_csv(sample_path)
    assert len(df) > 100
    assert "Sales" in df.columns
    assert "Region" in df.columns
