"""CSV Explorer - Interactive Exploratory Data Analysis (EDA) Web Application.

A modern, beginner-friendly, portfolio-quality data profiling dashboard built
with Streamlit, pandas, and Plotly.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from src.data_loader import (
    CSVEmptyError,
    CSVEncodingError,
    CSVParsingError,
    CSVSizeLimitExceededError,
    load_csv_detailed,
)
from src.data_overview import (
    classify_columns,
    get_column_metadata,
    get_column_sample_values,
    get_dataset_overview,
)
from src.data_quality import (
    IssueSeverity,
    generate_data_quality_report,
)
from src.export import (
    export_dataframe_to_csv,
    generate_json_report,
)
from src.outliers import detect_outliers_iqr
from src.statistics import (
    get_categorical_statistics,
    get_numeric_columns,
    get_numeric_statistics,
)
from src.visualizations import (
    create_box_plot,
    create_categorical_bar_chart,
    create_correlation_heatmap,
    create_histogram,
    create_missing_values_bar_chart,
)

# Application metadata
APP_TITLE = "CSV Explorer"
APP_VERSION = "1.0.0"
SAMPLE_DATA_PATH = Path("sample_data/sample_superstore_eda.csv")

# Set Streamlit page configuration
st.set_page_config(
    page_title=f"{APP_TITLE} • Modern EDA Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom SaaS Dark CSS Styles
CUSTOM_CSS = """
<style>
/* Modern typography and base styling */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Metric card styling */
div[data-testid="stMetric"] {
    background-color: #151923;
    border: 1px solid #293143;
    border-radius: 8px;
    padding: 14px 18px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

div[data-testid="stMetric"]:hover {
    border-color: #8B7CFF;
    transition: border-color 0.2s ease;
}

div[data-testid="stMetricLabel"] {
    color: #A3ADBD !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

div[data-testid="stMetricValue"] {
    color: #F5F7FA !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}

/* Card container helper */
.eda-card {
    background-color: #151923;
    border: 1px solid #293143;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 20px;
}

.eda-card-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: #F5F7FA;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.eda-card-subtitle {
    font-size: 0.88rem;
    color: #A3ADBD;
    margin-bottom: 16px;
}

/* Badges */
.badge-clean {
    background-color: rgba(54, 201, 143, 0.15);
    color: #36C98F;
    border: 1px solid rgba(54, 201, 143, 0.3);
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
}

.badge-warning {
    background-color: rgba(245, 185, 66, 0.15);
    color: #F5B942;
    border: 1px solid rgba(245, 185, 66, 0.3);
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
}

.badge-critical {
    background-color: rgba(240, 113, 120, 0.15);
    color: #F07178;
    border: 1px solid rgba(240, 113, 120, 0.3);
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
}

/* Hero container */
.hero-box {
    background: linear-gradient(145deg, #151923 0%, #1B2130 100%);
    border: 1px solid #293143;
    border-radius: 12px;
    padding: 32px 36px;
    margin-bottom: 24px;
}

.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #F5F7FA;
    margin-bottom: 8px;
}

.hero-subtitle {
    font-size: 1.15rem;
    color: #8B7CFF;
    font-weight: 500;
    margin-bottom: 12px;
}

.hero-desc {
    font-size: 0.95rem;
    color: #A3ADBD;
    line-height: 1.5;
    max-width: 820px;
}

/* Sidebar styling tweaks */
[data-testid="stSidebar"] {
    background-color: #10131B;
    border-right: 1px solid #293143;
}

/* Responsive table overflow */
div[data-testid="stDataFrame"] {
    border-radius: 8px;
    border: 1px solid #293143;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session_state() -> None:
    """Initialize persistent Streamlit session keys."""
    if "df" not in st.session_state:
        st.session_state["df"] = None
    if "dataset_name" not in st.session_state:
        st.session_state["dataset_name"] = None
    if "load_warnings" not in st.session_state:
        st.session_state["load_warnings"] = []
    if "current_nav" not in st.session_state:
        st.session_state["current_nav"] = "Overview"


init_session_state()


def handle_file_upload(uploaded_file: Any) -> None:
    """Process an uploaded file or sample dataset and update session state."""
    try:
        res = load_csv_detailed(uploaded_file)
        st.session_state["df"] = res.df
        st.session_state["dataset_name"] = res.metadata.filename
        st.session_state["load_warnings"] = res.metadata.warnings
        st.toast(f"Loaded '{res.metadata.filename}' successfully!", icon="✅")
    except CSVEmptyError as e:
        st.error(f"⚠️ Empty CSV Error: {str(e)}")
    except CSVSizeLimitExceededError as e:
        st.error(f"⛔ File Size Limit Exceeded: {str(e)}")
    except CSVParsingError as e:
        st.error(f"❌ Parsing Error: {str(e)}")
    except CSVEncodingError as e:
        st.error(f"🔤 Encoding Error: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred while loading the file: {str(e)}")


def load_sample_dataset() -> None:
    """Load the built-in sample Superstore dataset."""
    if SAMPLE_DATA_PATH.exists():
        handle_file_upload(SAMPLE_DATA_PATH)
    else:
        st.error("Sample dataset file not found on disk.")


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### 📊 CSV Explorer")
    st.caption("Interactive EDA & Data Profiling")
    st.divider()

    # Active dataset badge or indicator
    if st.session_state["df"] is not None:
        df_active = st.session_state["df"]
        st.markdown(f"**Dataset**: `{st.session_state['dataset_name']}`")
        st.caption(f"{len(df_active):,} rows × {len(df_active.columns):,} cols")

        if st.session_state["load_warnings"]:
            with st.expander("⚠️ Ingestion Notices", expanded=False):
                for w in st.session_state["load_warnings"]:
                    st.caption(f"• {w}")

        st.divider()

        # Primary Navigation
        nav_options = [
            "Overview",
            "Data Preview",
            "Data Quality",
            "Statistics",
            "Visualizations",
            "Outliers",
            "Export Report",
        ]
        selected_nav = st.radio(
            "Navigation",
            options=nav_options,
            index=nav_options.index(st.session_state["current_nav"])
            if st.session_state["current_nav"] in nav_options
            else 0,
            label_visibility="collapsed",
        )
        st.session_state["current_nav"] = selected_nav

        st.divider()

        # Upload / Replace dataset action
        st.markdown("#### Replace Dataset")
        new_file = st.file_uploader(
            "Upload new CSV",
            type=["csv"],
            key="replace_uploader",
            label_visibility="collapsed",
        )
        if new_file is not None:
            if new_file.name != st.session_state["dataset_name"]:
                handle_file_upload(new_file)
                st.rerun()

        if st.button("🔄 Reload Sample Data", use_container_width=True):
            load_sample_dataset()
            st.rerun()

        if st.button("🗑️ Clear Current Data", use_container_width=True):
            st.session_state["df"] = None
            st.session_state["dataset_name"] = None
            st.session_state["load_warnings"] = []
            st.rerun()
    else:
        st.info("No dataset currently loaded. Upload a CSV or load the sample data to get started.")
        if st.button("✨ Load Sample Dataset", use_container_width=True, type="primary"):
            load_sample_dataset()
            st.rerun()

    st.divider()

    # Privacy notice
    st.markdown("#### 🔒 Privacy Notice")
    st.caption(
        "Your CSV is processed by this application for analysis in memory. "
        "Do not upload confidential, personal, or sensitive information. "
        "Uploaded data is not stored persistently by this application."
    )

    st.markdown("---")
    st.caption(f"CSV Explorer v{APP_VERSION} • Built with Streamlit & Plotly")


# ============================================================
# MAIN CONTENT AREA
# ============================================================

df: pd.DataFrame | None = st.session_state["df"]

# ------------------------------------------------------------
# EMPTY STATE (WHEN NO DATASET LOADED)
# ------------------------------------------------------------
if df is None:
    st.markdown(
        """
        <div class="hero-box">
            <div class="hero-title">CSV Explorer</div>
            <div class="hero-subtitle">Understand your data before you build with it.</div>
            <div class="hero-desc">
                Upload a CSV file to explore its structure, identify data quality issues,
                discover patterns, and generate an interactive EDA report.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_upload, col_sample = st.columns([3, 2], gap="large")

    with col_upload:
        st.markdown(
            """
            <div class="eda-card">
                <div class="eda-card-title">📁 Upload Your Dataset</div>
                <div class="eda-card-subtitle">
                    Select a CSV file from your computer. Headers are expected in the first row.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded = st.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            key="home_uploader",
            help="Files are analyzed in memory up to 100 MB.",
        )
        if uploaded is not None:
            handle_file_upload(uploaded)
            st.rerun()

        st.caption(
            "ℹ️ Files are parsed strictly in memory. Supported encodings: UTF-8, UTF-8 BOM, Latin-1, CP1252."
        )

    with col_sample:
        st.markdown(
            """
            <div class="eda-card">
                <div class="eda-card-title">⚡ Try Built-in Sample Data</div>
                <div class="eda-card-subtitle">
                    Test all analysis features instantly with our curated e-commerce dataset.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            **Dataset Features**:
            - 122 transaction records & 16 columns
            - Realistic numeric, categorical, and date variables
            - Built-in data quality edge cases (nulls, duplicates, constant status)
            - Intentional positive and negative margin outliers
            """
        )
        if st.button("🚀 Load Sample Superstore Data", type="primary", use_container_width=True):
            load_sample_dataset()
            st.rerun()

    st.markdown("---")
    st.markdown("### 🛠️ What CSV Explorer Does For You")

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.markdown(
            """
            **1. Structural Overview**  
            Instant dimension profiling, memory usage, and automatic semantic column type classification.
            """
        )
    with f2:
        st.markdown(
            """
            **2. Data Quality Audit**  
            Transparent detection of missing cells, exact duplicated records, and constant zero-variance columns.
            """
        )
    with f3:
        st.markdown(
            """
            **3. Statistical Depth**  
            Rigorous numeric descriptive statistics (mean, median, IQR, skewness) and categorical mode distributions.
            """
        )
    with f4:
        st.markdown(
            """
            **4. Outliers & Visuals**  
            Interactive Plotly charts, correlation matrices, and mathematical IQR outlier detection with CSV/JSON export.
            """
        )

# ------------------------------------------------------------
# LOADED DATASET: SECTIONS
# ------------------------------------------------------------
else:
    section = st.session_state["current_nav"]

    # ========================================================
    # SECTION 1: OVERVIEW
    # ========================================================
    if section == "Overview":
        st.subheader("📊 Dataset Overview")
        st.caption(f"High-level structural audit of `{st.session_state['dataset_name']}`")

        overview = get_dataset_overview(df)

        # Primary Metric Cards
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Total Rows", f"{overview.total_rows:,}")
        m2.metric("Total Columns", f"{overview.total_columns:,}")
        m3.metric("Memory Usage", overview.memory_usage_formatted)
        m4.metric("Numeric Cols", len(overview.numeric_columns))
        m5.metric("Categorical Cols", len(overview.categorical_columns))
        m6.metric("Missing Cells", f"{overview.missing_cells_pct:.1f}%", help=f"{overview.total_missing_cells:,} total null cells")

        st.markdown("<br>", unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1], gap="medium")
        with col_left:
            st.markdown(
                """
                <div class="eda-card">
                    <div class="eda-card-title">🧩 Variable Type Breakdown</div>
                    <div class="eda-card-subtitle">Automatic semantic classification of column types</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write(
                f"- **Numeric ({len(overview.numeric_columns)})**: {', '.join(overview.numeric_columns) if overview.numeric_columns else 'None'}"
            )
            st.write(
                f"- **Categorical / Text ({len(overview.categorical_columns)})**: {', '.join(overview.categorical_columns) if overview.categorical_columns else 'None'}"
            )
            st.write(
                f"- **Datetime ({len(overview.datetime_columns)})**: {', '.join(overview.datetime_columns) if overview.datetime_columns else 'None'}"
            )
            st.write(
                f"- **Boolean ({len(overview.boolean_columns)})**: {', '.join(overview.boolean_columns) if overview.boolean_columns else 'None'}"
            )

        with col_right:
            st.markdown(
                """
                <div class="eda-card">
                    <div class="eda-card-title">⚡ Quick Dataset Summary</div>
                    <div class="eda-card-subtitle">Key dimensions and integrity markers</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write(f"- **Total Data Cells**: {overview.total_cells:,}")
            st.write(f"- **Missing Value Cells**: {overview.total_missing_cells:,} ({overview.missing_cells_pct}%)")
            st.write(f"- **Duplicate Rows**: {overview.total_duplicate_rows:,} ({overview.duplicate_rows_pct}%)")
            st.write(
                f"- **Clean Unique Observations**: {overview.total_rows - overview.total_duplicate_rows:,}"
            )

        st.markdown("### 📋 Column Metadata & Inferred Types")
        meta_df = get_column_metadata(df)
        st.dataframe(meta_df, use_container_width=True, hide_index=True)

    # ========================================================
    # SECTION 2: DATA PREVIEW
    # ========================================================
    elif section == "Data Preview":
        st.subheader("🔍 Data Preview & Column Inspection")
        st.caption(f"Inspect raw records and field distributions in `{st.session_state['dataset_name']}`")

        ctrl_col1, ctrl_col2 = st.columns([2, 4])
        with ctrl_col1:
            preview_rows = st.slider("Number of preview rows", min_value=5, max_value=100, value=10, step=5)
        with ctrl_col2:
            st.caption(f"Showing first {preview_rows} of {len(df):,} total rows across {len(df.columns)} columns.")

        st.dataframe(df.head(preview_rows), use_container_width=True)

        st.markdown("---")
        st.markdown("### 🔬 Inspect Individual Column")

        selected_col = st.selectbox("Choose a column to inspect", options=df.columns)
        if selected_col:
            col_series = df[selected_col]
            missing_count = int(col_series.isna().sum())
            missing_pct = round((missing_count / len(df)) * 100.0, 2)
            unique_count = int(col_series.nunique(dropna=True))
            sample_values = get_column_sample_values(df, selected_col, n_samples=8)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Column Name", str(selected_col))
            c2.metric("Pandas Dtype", str(col_series.dtype))
            c3.metric("Missing Count", f"{missing_count:,} ({missing_pct}%)")
            c4.metric("Unique Values", f"{unique_count:,}")

            st.markdown("**Sample Non-Null Values**:")
            st.write(sample_values)

    # ========================================================
    # SECTION 3: DATA QUALITY
    # ========================================================
    elif section == "Data Quality":
        st.subheader("🛡️ Data Quality Diagnostic Audit")
        st.caption("Automatic diagnostic evaluation of null entries, duplicates, and column variances.")

        threshold_val = st.slider(
            "Nearly-empty column threshold (% missing)",
            min_value=50.0,
            max_value=99.0,
            value=90.0,
            step=5.0,
            help="Columns exceeding this threshold of missing values will be flagged as nearly empty.",
        )

        quality_report = generate_data_quality_report(df, nearly_empty_threshold_pct=threshold_val)

        # Status and Score Banner
        b1, b2, b3 = st.columns([2, 2, 4])
        with b1:
            if "No major issues" in quality_report.status:
                badge_html = f'<span class="badge-clean">{quality_report.status}</span>'
            elif "Some issues" in quality_report.status:
                badge_html = f'<span class="badge-warning">{quality_report.status}</span>'
            else:
                badge_html = f'<span class="badge-critical">{quality_report.status}</span>'
            st.markdown(f"**Overall Status**<br>{badge_html}", unsafe_allow_html=True)
        with b2:
            st.metric("Quality Health Score", f"{quality_report.overall_health_score}/100")
        with b3:
            st.caption(
                "Health score is a transparent diagnostic heuristic evaluating missing cells, "
                "duplicated rows, constant columns, and empty columns. Original data is never altered."
            )

        st.markdown("<br>", unsafe_allow_html=True)

        if quality_report.issues:
            st.markdown("#### ⚠️ Identified Quality Issues")
            for issue in quality_report.issues:
                sev_color = "#36C98F" if issue.severity == IssueSeverity.INFO else ("#F5B942" if issue.severity == IssueSeverity.WARNING else "#F07178")
                st.markdown(
                    f"""
                    <div style="border-left: 4px solid {sev_color}; padding-left: 14px; margin-bottom: 12px; background: #151923; padding: 12px 16px; border-radius: 4px;">
                        <strong style="color: #F5F7FA;">{issue.title}</strong> [{issue.severity.value}]<br>
                        <span style="color: #A3ADBD; font-size: 0.9rem;">{issue.description}</span>
                        {f'<br><span style="color: #8B7CFF; font-size: 0.85rem;">Affected: {", ".join(issue.affected_columns)}</span>' if issue.affected_columns else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("🎉 Excellent! No quality issues detected in this dataset.")

        st.divider()

        # Subsection A: Missing Values
        st.markdown("### 1. Missing Values Analysis")
        m_sum = quality_report.missing_summary

        if m_sum.columns_with_missing_count > 0:
            fig_missing = create_missing_values_bar_chart(m_sum.detail_table)
            st.plotly_chart(fig_missing, use_container_width=True)

            show_all_cols = st.checkbox("Show all columns (including 0% missing)", value=False)
            table_to_show = m_sum.detail_table if show_all_cols else m_sum.detail_table[m_sum.detail_table["Missing Count"] > 0]
            st.dataframe(table_to_show, use_container_width=True, hide_index=True)
        else:
            st.info("No missing values detected. Every column in this dataset is 100% complete!")

        st.divider()

        # Subsection B: Duplicate Rows
        st.markdown("### 2. Duplicate Rows Analysis")
        d_sum = quality_report.duplicate_summary
        d1, d2, d3 = st.columns(3)
        d1.metric("Duplicate Rows", f"{d_sum.total_duplicates:,}")
        d2.metric("Duplicate Percentage", f"{d_sum.duplicate_pct:.2f}%")
        d3.metric("Rows Remaining if Deduped", f"{d_sum.rows_remaining_after_dedup:,}")

        if d_sum.total_duplicates > 0:
            st.markdown("**Preview of Duplicated Rows**:")
            st.dataframe(d_sum.duplicate_rows_preview, use_container_width=True)
            st.caption("Notice: CSV Explorer only audits duplicate rows. Your dataset has not been modified.")
        else:
            st.info("No duplicate rows found. Every record is unique.")

        st.divider()

        # Subsection C: Column Variances
        st.markdown("### 3. Constant & Empty Columns")
        v_sum = quality_report.variance_summary
        v1, v2, v3 = st.columns(3)
        v1.metric("Constant Columns", len(v_sum.constant_columns))
        v2.metric("Nearly Empty Cols", len(v_sum.nearly_empty_columns))
        v3.metric("Entirely Empty Cols", len(v_sum.entirely_empty_columns))

        if v_sum.constant_columns:
            st.warning(f"Constant columns detected: {list(v_sum.constant_columns.keys())}")
            for c_name, c_val in v_sum.constant_columns.items():
                st.write(f"- **`{c_name}`**: Constant value is `'{c_val}'`. Provides zero variance for analytics.")

        if v_sum.nearly_empty_columns:
            st.warning(f"Nearly empty columns (≥ {threshold_val}% missing): {v_sum.nearly_empty_columns}")

        if v_sum.entirely_empty_columns:
            st.error(f"Entirely empty columns (100% missing): {v_sum.entirely_empty_columns}")

    # ========================================================
    # SECTION 4: STATISTICS
    # ========================================================
    elif section == "Statistics":
        st.subheader("📈 Statistical Analysis")
        st.caption("Descriptive statistics for numeric variables and frequency distributions for categorical variables.")

        stat_tab_num, stat_tab_cat = st.tabs(["🔢 Numeric Descriptive Statistics", "🔤 Categorical Frequency Analysis"])

        with stat_tab_num:
            num_cols = get_numeric_columns(df)
            if not num_cols:
                st.warning("No numeric columns detected in this dataset.")
            else:
                selected_num = st.multiselect(
                    "Filter numeric columns to display",
                    options=num_cols,
                    default=num_cols,
                )
                if selected_num:
                    stats_table = get_numeric_statistics(df, columns=selected_num)
                    st.dataframe(stats_table, use_container_width=True, hide_index=True)

                    csv_stats_bytes = export_dataframe_to_csv(stats_table)
                    st.download_button(
                        label="📥 Download Numeric Statistics (CSV)",
                        data=csv_stats_bytes,
                        file_name=f"{st.session_state['dataset_name']}_numeric_statistics.csv",
                        mime="text/csv",
                    )
                else:
                    st.info("Select at least one numeric column above.")

                with st.expander("💡 Data Science Mentor: Understanding Descriptive Metrics", expanded=False):
                    st.markdown(
                        """
                        - **Mean vs Median**: The mean is the mathematical average (sensitive to extreme outliers). The median is the 50th percentile value (resistant to outliers). When mean and median diverge, the distribution is skewed.
                        - **Standard Deviation & Variance**: Measure the spread of observations around the mean.
                        - **IQR (Interquartile Range)**: Distance between the 25th percentile (Q1) and 75th percentile (Q3). Measures the spread of the middle 50% of the data.
                        - **Skewness**: Positive indicates a long right tail (higher values); negative indicates a long left tail.
                        """
                    )

        with stat_tab_cat:
            cat_cols = [c for c in df.columns if c not in get_numeric_columns(df) and not pd.api.types.is_bool_dtype(df[c])]
            if not cat_cols:
                # If no strict object column, allow selecting any column
                cat_cols = list(df.columns)

            chosen_cat = st.selectbox("Select categorical column", options=cat_cols)
            top_k = st.slider("Top categories to display", min_value=5, max_value=30, value=10, step=5)

            if chosen_cat:
                cat_stats = get_categorical_statistics(df, chosen_cat, top_n=top_k)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Observations", f"{cat_stats.total_observations:,}")
                c2.metric("Missing Count", f"{cat_stats.missing_observations:,} ({cat_stats.missing_pct}%)")
                c3.metric("Unique Categories", f"{cat_stats.unique_count:,}")
                c4.metric(
                    "Most Frequent (Mode)",
                    f"{cat_stats.most_frequent_value}",
                    help=f"{cat_stats.most_frequent_count:,} occurrences ({cat_stats.most_frequent_pct}%)",
                )

                st.markdown(f"**Top {len(cat_stats.frequency_table)} Frequency Distribution Table**:")
                st.dataframe(cat_stats.frequency_table, use_container_width=True, hide_index=True)

                if cat_stats.total_distinct_omitted > 0:
                    st.caption(
                        f"ℹ️ Notice: {cat_stats.total_distinct_omitted:,} additional distinct categories are omitted from this top-{top_k} display."
                    )

                csv_freq_bytes = export_dataframe_to_csv(cat_stats.frequency_table)
                st.download_button(
                    label=f"📥 Download '{chosen_cat}' Frequencies (CSV)",
                    data=csv_freq_bytes,
                    file_name=f"{chosen_cat}_frequencies.csv",
                    mime="text/csv",
                )

    # ========================================================
    # SECTION 5: VISUALIZATIONS
    # ========================================================
    elif section == "Visualizations":
        st.subheader("📉 Interactive Visualizations")
        st.caption("Responsive Plotly charts rendered directly from your uploaded data.")

        vtab_hist, vtab_box, vtab_bar, vtab_corr = st.tabs([
            "📊 Histogram",
            "📦 Box Plot",
            "📶 Categorical Bar Chart",
            "🔥 Correlation Heatmap",
        ])

        with vtab_hist:
            num_cols = get_numeric_columns(df)
            if not num_cols:
                st.warning("No numeric columns available to plot histograms.")
            else:
                col_sel_h, col_bins_h, col_lines_h = st.columns([3, 2, 2])
                with col_sel_h:
                    hist_col = st.selectbox("Select numeric column", options=num_cols, key="hist_col_select")
                with col_bins_h:
                    n_bins = st.slider("Number of bins", min_value=5, max_value=80, value=25, step=5)
                with col_lines_h:
                    show_lines = st.checkbox("Show Mean & Median", value=True)

                if hist_col:
                    fig_hist = create_histogram(df, hist_col, nbins=n_bins, show_mean_median=show_lines)
                    st.plotly_chart(fig_hist, use_container_width=True)
                    st.info(
                        f"💡 A histogram shows how frequently numeric values in **{hist_col}** fall into different ranges."
                    )

        with vtab_box:
            num_cols = get_numeric_columns(df)
            if not num_cols:
                st.warning("No numeric columns available for box plots.")
            else:
                col_b1, col_b2 = st.columns([3, 2])
                with col_b1:
                    box_col = st.selectbox("Select numeric column", options=num_cols, key="box_col_select")
                with col_b2:
                    points_opt = st.selectbox("Points display", options=["outliers", "all", False], index=0)

                if box_col:
                    fig_box = create_box_plot(df, box_col, points_mode=points_opt)
                    st.plotly_chart(fig_box, use_container_width=True)
                    st.info(
                        f"💡 The box plot shows the median line, upper/lower quartiles (Q1, Q3), "
                        f"whiskers, and potential outlier points in **{box_col}**. Outliers require analytical investigation."
                    )

        with vtab_bar:
            all_cols = list(df.columns)
            col_bar1, col_bar2 = st.columns([3, 2])
            with col_bar1:
                bar_col = st.selectbox("Select column", options=all_cols, key="bar_col_select")
            with col_bar2:
                bar_top_n = st.slider("Top categories to display", min_value=3, max_value=30, value=10, step=1)

            if bar_col:
                fig_bar = create_categorical_bar_chart(df, bar_col, top_n=bar_top_n)
                st.plotly_chart(fig_bar, use_container_width=True)

        with vtab_corr:
            num_cols = get_numeric_columns(df)
            if len(num_cols) < 2:
                st.warning("Need at least 2 numeric columns to compute correlations.")
            else:
                corr_c1, corr_c2 = st.columns([4, 2])
                with corr_c1:
                    selected_corr_cols = st.multiselect(
                        "Select columns for correlation matrix",
                        options=num_cols,
                        default=num_cols[: min(8, len(num_cols))],
                    )
                with corr_c2:
                    corr_method = st.selectbox("Method", options=["pearson", "spearman"], index=0)

                if len(selected_corr_cols) >= 2:
                    fig_corr = create_correlation_heatmap(df, columns=selected_corr_cols, method=corr_method)
                    st.plotly_chart(fig_corr, use_container_width=True)
                    st.info(
                        "💡 **Mentor Note**: Correlation measures linear association between -1.0 (strong inverse) "
                        "and +1.0 (strong direct). Correlation does **not** imply causation!"
                    )
                else:
                    st.info("Select at least 2 columns to calculate correlation.")

    # ========================================================
    # SECTION 6: OUTLIERS
    # ========================================================
    elif section == "Outliers":
        st.subheader("🎯 Outlier Detection (Interquartile Range Method)")
        st.caption("Mathematical IQR outlier detection identifying observations outside expected statistical spread.")

        with st.expander("📐 How the Interquartile Range (IQR) Rule Works", expanded=True):
            st.markdown(
                """
                1. **First Quartile (Q1)**: 25th percentile of valid observations.
                2. **Third Quartile (Q3)**: 75th percentile of valid observations.
                3. **IQR**: $\\text{IQR} = Q3 - Q1$.
                4. **Lower Bound**: $Q1 - (1.5 \\times \\text{IQR})$.
                5. **Upper Bound**: $Q3 + (1.5 \\times \\text{IQR})$.

                Values falling strictly below the lower bound or above the upper bound are flagged as potential outliers.  
                *Important: Outliers are mathematical flags, not necessarily data entry errors. They often highlight high-value sales, critical system spikes, or rare phenomena.*
                """
            )

        num_cols = get_numeric_columns(df)
        if not num_cols:
            st.warning("No numeric columns available for outlier detection.")
        else:
            col_o1, col_o2 = st.columns([3, 2])
            with col_o1:
                target_outlier_col = st.selectbox("Select numeric column", options=num_cols)
            with col_o2:
                multiplier_choice = st.select_slider(
                    "IQR Multiplier",
                    options=[1.5, 2.0, 2.5, 3.0],
                    value=1.5,
                    help="1.5 identifies standard outliers; 3.0 identifies extreme outliers.",
                )

            if target_outlier_col:
                outlier_res = detect_outliers_iqr(df, target_outlier_col, multiplier=multiplier_choice)

                # Metrics row
                o1, o2, o3, o4, o5 = st.columns(5)
                o1.metric("Lower Bound", f"{outlier_res.lower_bound:.2f}" if outlier_res.lower_bound is not None else "N/A")
                o2.metric("Upper Bound", f"{outlier_res.upper_bound:.2f}" if outlier_res.upper_bound is not None else "N/A")
                o3.metric("IQR", f"{outlier_res.iqr:.2f}" if outlier_res.iqr is not None else "N/A")
                o4.metric("Flagged Outliers", f"{outlier_res.flagged_count:,}")
                o5.metric("Flagged Share", f"{outlier_res.flagged_pct:.2f}%")

                st.caption(outlier_res.status_message)

                # Visual inspection box plot
                st.plotly_chart(create_box_plot(df, target_outlier_col, points_mode="outliers"), use_container_width=True)

                if outlier_res.flagged_count > 0:
                    st.markdown(f"**Preview of Flagged Outlier Records ({outlier_res.flagged_count:,} rows)**:")
                    st.dataframe(outlier_res.flagged_df, use_container_width=True)

                    outlier_csv_bytes = export_dataframe_to_csv(outlier_res.flagged_df)
                    st.download_button(
                        label=f"📥 Download Flagged Outliers for '{target_outlier_col}' (CSV)",
                        data=outlier_csv_bytes,
                        file_name=f"{target_outlier_col}_outliers.csv",
                        mime="text/csv",
                    )
                else:
                    st.info(f"No observations in '{target_outlier_col}' fell outside the calculated IQR boundaries.")

    # ========================================================
    # SECTION 7: EXPORT REPORT
    # ========================================================
    elif section == "Export Report":
        st.subheader("💾 Export Analysis & Reports")
        st.caption("Download your exploratory analysis as standalone CSV tables or a consolidated JSON audit report.")

        overview = get_dataset_overview(df)
        quality_report = generate_data_quality_report(df)
        meta_df = get_column_metadata(df)
        num_stats_df = get_numeric_statistics(df)

        exp_col1, exp_col2 = st.columns([1, 1], gap="large")

        with exp_col1:
            st.markdown(
                """
                <div class="eda-card">
                    <div class="eda-card-title">📄 CSV Table Exports</div>
                    <div class="eda-card-subtitle">Download clean tabular summaries for spreadsheets or presentations</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # 1. Dataset Overview / Metadata
            overview_csv = export_dataframe_to_csv(meta_df)
            st.download_button(
                "📥 Column Metadata & Overview (CSV)",
                data=overview_csv,
                file_name=f"{st.session_state['dataset_name']}_column_metadata.csv",
                mime="text/csv",
                use_container_width=True,
            )

            # 2. Data Quality Table
            quality_csv = export_dataframe_to_csv(quality_report.missing_summary.detail_table)
            st.download_button(
                "📥 Missing Values Audit (CSV)",
                data=quality_csv,
                file_name=f"{st.session_state['dataset_name']}_missing_values.csv",
                mime="text/csv",
                use_container_width=True,
            )

            # 3. Numeric Statistics Table
            if not num_stats_df.empty:
                stats_csv = export_dataframe_to_csv(num_stats_df)
                st.download_button(
                    "📥 Numeric Descriptive Statistics (CSV)",
                    data=stats_csv,
                    file_name=f"{st.session_state['dataset_name']}_numeric_statistics.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            # 4. Duplicate Rows (if any)
            if quality_report.duplicate_summary.total_duplicates > 0:
                dup_csv = export_dataframe_to_csv(quality_report.duplicate_summary.duplicate_rows_preview)
                st.download_button(
                    "📥 Flagged Duplicate Rows (CSV)",
                    data=dup_csv,
                    file_name=f"{st.session_state['dataset_name']}_duplicate_rows.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        with exp_col2:
            st.markdown(
                """
                <div class="eda-card">
                    <div class="eda-card-title">📦 Consolidated JSON EDA Report</div>
                    <div class="eda-card-subtitle">
                        Comprehensive programmatic audit summary including dimensions, data quality, and statistics.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Prepare report dictionary
            overview_dict = {
                "total_rows": overview.total_rows,
                "total_columns": overview.total_columns,
                "total_cells": overview.total_cells,
                "memory_usage_formatted": overview.memory_usage_formatted,
                "numeric_columns_count": len(overview.numeric_columns),
                "categorical_columns_count": len(overview.categorical_columns),
                "total_missing_cells": overview.total_missing_cells,
                "missing_cells_pct": overview.missing_cells_pct,
                "total_duplicate_rows": overview.total_duplicate_rows,
            }

            quality_dict = {
                "status": quality_report.status,
                "health_score": quality_report.overall_health_score,
                "total_missing_cells": quality_report.missing_summary.total_missing_cells,
                "missing_cells_pct": quality_report.missing_summary.missing_cells_pct,
                "duplicate_rows_count": quality_report.duplicate_summary.total_duplicates,
                "constant_columns": list(quality_report.variance_summary.constant_columns.keys()),
                "nearly_empty_columns": quality_report.variance_summary.nearly_empty_columns,
                "entirely_empty_columns": quality_report.variance_summary.entirely_empty_columns,
                "issues": [
                    {"title": iss.title, "severity": iss.severity.value, "description": iss.description}
                    for iss in quality_report.issues
                ],
            }

            json_report_str = generate_json_report(
                filename=st.session_state["dataset_name"],
                overview_dict=overview_dict,
                column_metadata_df=meta_df,
                quality_summary_dict=quality_dict,
                numeric_stats_df=num_stats_df,
            )

            st.download_button(
                "📥 Download Consolidated JSON Report",
                data=json_report_str.encode("utf-8"),
                file_name=f"{st.session_state['dataset_name']}_eda_report.json",
                mime="application/json",
                type="primary",
                use_container_width=True,
            )

            with st.expander("👁️ Preview JSON Report Content", expanded=False):
                st.json(json_report_str)
