"""Unit tests for src/visualizations.py."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from src.visualizations import (
    create_histogram,
    create_box_plot,
    create_categorical_bar_chart,
    create_correlation_heatmap,
    create_missing_values_bar_chart,
)


def test_create_histogram():
    df = pd.DataFrame({"age": [20, 25, 30, 35, 40, 45, 50]})
    fig = create_histogram(df, "age", nbins=10, show_mean_median=True)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1
    assert fig.data[0].type == "histogram"


def test_create_box_plot():
    df = pd.DataFrame({"income": [30000, 40000, 50000, 60000, 150000]})
    fig = create_box_plot(df, "income", points_mode="outliers")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1
    assert fig.data[0].type == "box"


def test_create_categorical_bar_chart():
    df = pd.DataFrame({"city": ["London", "Paris", "London", "Tokyo", "London"]})
    fig = create_categorical_bar_chart(df, "city", top_n=5)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1
    assert fig.data[0].type == "bar"


def test_create_correlation_heatmap_valid():
    df = pd.DataFrame({
        "sales": [100, 200, 300, 400],
        "profit": [10, 25, 35, 50],
        "discount": [0.1, 0.2, 0.1, 0.3],
    })
    fig = create_correlation_heatmap(df, columns=["sales", "profit", "discount"])
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1
    assert fig.data[0].type == "heatmap"


def test_create_correlation_heatmap_insufficient_cols():
    df = pd.DataFrame({"sales": [100, 200, 300]})
    fig = create_correlation_heatmap(df, columns=["sales"])
    assert isinstance(fig, go.Figure)
    # Renders message annotation gracefully rather than failing
    assert len(fig.layout.annotations) > 0


def test_create_missing_values_bar_chart():
    table = pd.DataFrame({
        "Column": ["age", "income"],
        "Missing Count": [2, 0],
        "Missing %": [20.0, 0.0],
    })
    fig = create_missing_values_bar_chart(table)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1
    assert fig.data[0].type == "bar"
