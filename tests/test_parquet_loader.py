"""Unit tests for Analytix Parquet columnar data loader."""

import io
import pytest
import pandas as pd

from src.parquet_loader import (
    ParquetEmptyError,
    ParquetParsingError,
    load_parquet_detailed,
)


def test_load_parquet_valid():
    """Verify loading valid Parquet file created from pandas."""
    df_orig = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "metric": [10.5, 20.0, 35.8],
            "status": ["active", "pending", "active"],
        }
    )
    buf = io.BytesIO()
    df_orig.to_parquet(buf, engine="pyarrow", index=False)
    buf.seek(0)

    res = load_parquet_detailed(buf)
    assert len(res.df) == 3
    assert list(res.df.columns) == ["id", "metric", "status"]
    assert res.df["metric"].iloc[1] == 20.0
    assert res.metadata.encoding_used == "parquet/binary"


def test_load_parquet_empty_error():
    """Verify empty bytes raise ParquetEmptyError."""
    with pytest.raises(ParquetEmptyError):
        load_parquet_detailed(io.BytesIO(b""))


def test_load_parquet_corrupted_error():
    """Verify corrupted non-parquet bytes raise ParquetParsingError."""
    with pytest.raises(ParquetParsingError):
        load_parquet_detailed(io.BytesIO(b"PAR1_NOT_VALID_PARQUET_DATA"))
