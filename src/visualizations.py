"""Interactive Plotly data visualizations for CSV Explorer.

Provides:
- Distribution histograms with configurable bins and mean/median indicators
- Interactive box plots displaying quartiles and spread
- Categorical frequency bar charts with top-N filtering
- Correlation heatmaps with Pearson/Spearman options and safe handling of low variance
- Missing values percentage horizontal bar charts
- Dark minimalist theme matching the design system
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Design system color palette
BG_DARK = "#0A0B10"
CARD_BG = "#151824"
PLOT_BG = "#10121A"
BORDER_COLOR = "#292E3D"
TEXT_PRIMARY = "#F5F6FA"
TEXT_MUTED = "#A3A9BA"
ACCENT_PRIMARY = "#8B7CFF"
ACCENT_SECONDARY = "#4DD8C7"
ACCENT_WARNING = "#F3BB57"
ACCENT_ERROR = "#F07885"


def apply_theme(fig: go.Figure, title: str = "", height: int = 420) -> go.Figure:
    """Apply the unified dark SaaS styling template to any Plotly figure.

    Args:
        fig: Plotly figure to style.
        title: Chart title.
        height: Height in pixels.

    Returns:
        go.Figure: Styled figure.
    """
    fig.update_layout(
        title={
            "text": title,
            "font": {"size": 15, "color": TEXT_PRIMARY, "family": "Inter, sans-serif"},
            "x": 0.01,
            "xanchor": "left",
        },
        paper_bgcolor=CARD_BG,
        plot_bgcolor=PLOT_BG,
        font={"color": TEXT_MUTED, "family": "Inter, -apple-system, sans-serif"},
        height=height,
        margin={"l": 50, "r": 30, "t": 60, "b": 50},
        hoverlabel={
            "bgcolor": "#1B2130",
            "font_size": 12,
            "font_family": "Inter, sans-serif",
            "font_color": TEXT_PRIMARY,
            "bordercolor": BORDER_COLOR,
        },
        xaxis={
            "gridcolor": BORDER_COLOR,
            "zerolinecolor": BORDER_COLOR,
            "tickfont": {"color": TEXT_MUTED},
            "title_font": {"color": TEXT_PRIMARY},
        },
        yaxis={
            "gridcolor": BORDER_COLOR,
            "zerolinecolor": BORDER_COLOR,
            "tickfont": {"color": TEXT_MUTED},
            "title_font": {"color": TEXT_PRIMARY},
        },
        legend={
            "font": {"color": TEXT_PRIMARY},
            "bgcolor": "rgba(0,0,0,0)",
        },
    )
    return fig


def create_histogram(
    df: pd.DataFrame,
    column: str,
    nbins: int = 30,
    show_mean_median: bool = True,
) -> go.Figure:
    """Create an interactive distribution histogram for a numeric column.

    Args:
        df: Input DataFrame.
        column: Numeric column name.
        nbins: Number of histogram bins.
        show_mean_median: Whether to add vertical mean and median indicator lines.

    Returns:
        go.Figure: Interactive histogram figure.
    """
    clean_series = df[column].dropna()
    if clean_series.empty:
        fig = go.Figure()
        fig.add_annotation(text="No valid numeric observations to display", showarrow=False)
        return apply_theme(fig, title=f"Distribution of {column}")

    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=clean_series,
            nbinsx=nbins,
            name=column,
            marker={
                "color": ACCENT_PRIMARY,
                "line": {"color": "#6C5CE7", "width": 1},
            },
            opacity=0.85,
            hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>",
        )
    )

    if show_mean_median and len(clean_series) > 1:
        mean_val = float(clean_series.mean())
        median_val = float(clean_series.median())

        fig.add_vline(
            x=mean_val,
            line_dash="dash",
            line_color=ACCENT_SECONDARY,
            annotation_text=f"Mean: {mean_val:.2f}",
            annotation_position="top right",
            annotation_font={"color": ACCENT_SECONDARY, "size": 11},
        )
        fig.add_vline(
            x=median_val,
            line_dash="dot",
            line_color=ACCENT_WARNING,
            annotation_text=f"Median: {median_val:.2f}",
            annotation_position="top left",
            annotation_font={"color": ACCENT_WARNING, "size": 11},
        )

    fig.update_layout(
        xaxis_title=column,
        yaxis_title="Frequency Count",
        bargap=0.08,
    )
    return apply_theme(fig, title=f"Distribution of {column}")


def create_box_plot(
    df: pd.DataFrame,
    column: str,
    points_mode: str = "outliers",
) -> go.Figure:
    """Generate an interactive box plot showing quartiles, spread, and outliers.

    Args:
        df: Input DataFrame.
        column: Numeric column name.
        points_mode: Points display option ('outliers', 'all', False).

    Returns:
        go.Figure: Interactive box plot figure.
    """
    clean_series = df[column].dropna()
    if clean_series.empty:
        fig = go.Figure()
        fig.add_annotation(text="No valid numeric data to display", showarrow=False)
        return apply_theme(fig, title=f"Box Plot: {column}")

    fig = go.Figure()
    fig.add_trace(
        go.Box(
            y=clean_series,
            name=column,
            boxpoints=points_mode,
            jitter=0.3,
            pointpos=-1.8,
            marker={
                "color": ACCENT_SECONDARY,
                "size": 5,
                "outliercolor": ACCENT_ERROR,
            },
            line={"color": ACCENT_PRIMARY, "width": 2},
            fillcolor="rgba(139, 124, 255, 0.2)",
            hovertemplate="Value: %{y}<extra></extra>",
        )
    )

    fig.update_layout(
        yaxis_title=column,
        xaxis_showticklabels=False,
    )
    return apply_theme(fig, title=f"Box Plot: {column}")


def create_categorical_bar_chart(
    df: pd.DataFrame,
    column: str,
    top_n: int = 10,
) -> go.Figure:
    """Generate an interactive bar chart of category frequencies.

    Args:
        df: Input DataFrame.
        column: Categorical column name.
        top_n: Number of most frequent categories to display.

    Returns:
        go.Figure: Interactive bar chart.
    """
    valid_series = df[column].dropna()
    if valid_series.empty:
        fig = go.Figure()
        fig.add_annotation(text="No valid categorical observations to display", showarrow=False)
        return apply_theme(fig, title=f"Frequencies: {column}")

    counts = valid_series.value_counts(dropna=True).head(top_n)
    total_valid = len(valid_series)
    pcts = [round((c / total_valid) * 100.0, 1) for c in counts.values]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=[str(idx) for idx in counts.index],
            y=counts.values,
            text=[f"{c} ({p}%)" for c, p in zip(counts.values, pcts)],
            textposition="auto",
            marker={
                "color": ACCENT_PRIMARY,
                "line": {"color": "#6C5CE7", "width": 1},
            },
            hovertemplate="Category: %{x}<br>Count: %{y}<br>Share: %{customdata}%<extra></extra>",
            customdata=pcts,
        )
    )

    fig.update_layout(
        xaxis_title=column,
        yaxis_title="Observation Count",
        xaxis_tickangle=-30 if len(counts) > 5 else 0,
    )
    return apply_theme(fig, title=f"Top {len(counts)} Categories in {column}")


def create_correlation_heatmap(
    df: pd.DataFrame,
    columns: Optional[list[str]] = None,
    method: str = "pearson",
) -> go.Figure:
    """Generate an interactive correlation heatmap for numeric columns.

    Args:
        df: Input DataFrame.
        columns: Optional subset of numeric columns.
        method: Correlation method ('pearson' or 'spearman').

    Returns:
        go.Figure: Correlation heatmap figure.
    """
    if columns is None:
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_bool_dtype(df[c])]
    else:
        numeric_cols = [c for c in columns if c in df.columns]

    # Filter out constant columns with 0 variance as correlation is undefined
    usable_cols = [c for c in numeric_cols if df[c].dropna().nunique() > 1]

    if len(usable_cols) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Need at least 2 non-constant numeric columns to calculate correlation.",
            showarrow=False,
            font={"size": 13, "color": TEXT_MUTED},
        )
        return apply_theme(fig, title="Correlation Matrix (Insufficient Data)")

    corr_matrix = df[usable_cols].corr(method=method)

    # Round correlation coefficients for clean hover and text display
    rounded_corr = corr_matrix.round(2)
    z_values = rounded_corr.values
    x_labels = [str(c) for c in usable_cols]
    y_labels = [str(c) for c in usable_cols]

    # Custom Diverging Color Scale: Teal -> Dark Neutral -> Purple
    custom_colorscale = [
        [0.0, ACCENT_SECONDARY],  # Negative correlation (-1.0)
        [0.5, CARD_BG],           # Zero correlation (0.0)
        [1.0, ACCENT_PRIMARY],    # Positive correlation (+1.0)
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=x_labels,
            y=y_labels,
            colorscale=custom_colorscale,
            zmin=-1.0,
            zmax=1.0,
            text=np.where(np.isnan(z_values), "N/A", z_values.astype(str)),
            texttemplate="%{text}",
            textfont={"size": 12, "color": TEXT_PRIMARY},
            hoverongaps=False,
            hovertemplate="Pair: %{x} & %{y}<br>Correlation: %{z:.2f}<extra></extra>",
            colorbar={
                "title": f"{method.capitalize()}<br>Corr",
                "tickvals": [-1.0, -0.5, 0.0, 0.5, 1.0],
                "ticktext": ["-1.0", "-0.5", "0.0", "0.5", "1.0"],
                "tickfont": {"color": TEXT_MUTED},
            },
        )
    )

    fig.update_layout(
        xaxis={"tickangle": -35},
        yaxis={"autorange": "reversed"},
    )
    return apply_theme(fig, title=f"Correlation Heatmap ({method.capitalize()} Method)", height=480)


def create_missing_values_bar_chart(detail_table: pd.DataFrame) -> go.Figure:
    """Generate a horizontal bar chart of missing value percentages.

    Args:
        detail_table: DataFrame containing 'Column' and 'Missing %'.

    Returns:
        go.Figure: Horizontal bar chart figure.
    """
    # Filter to columns that actually have missing values
    missing_only = detail_table[detail_table["Missing %"] > 0].copy()

    if missing_only.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Clean dataset: Zero missing values detected across all columns!",
            showarrow=False,
            font={"size": 14, "color": "#36C98F"},
        )
        return apply_theme(fig, title="Missing Values Analysis (All Complete)")

    missing_only = missing_only.sort_values(by="Missing %", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=missing_only["Column"],
            x=missing_only["Missing %"],
            orientation="h",
            marker={
                "color": ACCENT_ERROR,
                "opacity": 0.85,
            },
            text=[f"{p:.1f}% ({c:,} nulls)" for p, c in zip(missing_only["Missing %"], missing_only["Missing Count"])],
            textposition="auto",
            hovertemplate="Column: %{y}<br>Missing: %{x:.2f}%<extra></extra>",
        )
    )

    fig.update_layout(
        xaxis_title="Missing Values (%)",
        xaxis_range=[0, max(100, float(missing_only["Missing %"].max()) + 5)],
        yaxis_title="Column",
    )
    return apply_theme(fig, title="Missing Value Percentages by Column")
