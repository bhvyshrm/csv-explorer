"""Analytix - Multi-Format Data Exploration Platform.

A modern, SaaS-grade exploratory data analysis dashboard supporting CSV files
and multi-sheet Excel workbooks (.xlsx, .xls) built with Streamlit, pandas,
and Plotly.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Optional

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
from src.excel_loader import (
    ExcelCorruptedError,
    ExcelEmptySheetError,
    ExcelEmptyWorkbookError,
    ExcelSheetNotFoundError,
    ExcelUnsupportedFormatError,
    WorkbookMetadata,
    inspect_excel_workbook,
    load_excel_sheet,
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
APP_TITLE = "Analytix"
APP_TAGLINE = "Explore data. Discover insights."
APP_VERSION = "2.0.0"

SAMPLE_CSV_PATH = Path("sample_data/sample_superstore_eda.csv")
SAMPLE_EXCEL_PATH = Path("sample_data/sample_analytix_multisheet.xlsx")

# Set Streamlit page configuration
st.set_page_config(
    page_title=f"{APP_TITLE} • {APP_TAGLINE}",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Analytix Modern Theme Styles
CUSTOM_CSS = """
<style>
/* Typography & Base Reset */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #F5F6FA;
}

/* Metric Cards */
div[data-testid="stMetric"] {
    background-color: #151824;
    border: 1px solid #292E3D;
    border-radius: 8px;
    padding: 14px 18px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
}

div[data-testid="stMetric"]:hover {
    border-color: #8B7CFF;
    transition: border-color 0.2s ease;
}

div[data-testid="stMetricLabel"] {
    color: #A3A9BA !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

div[data-testid="stMetricValue"] {
    color: #F5F6FA !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
}

/* Card Container */
.analytix-card {
    background-color: #151824;
    border: 1px solid #292E3D;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 20px;
}

.analytix-card-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: #F5F6FA;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.analytix-card-subtitle {
    font-size: 0.88rem;
    color: #A3A9BA;
    margin-bottom: 14px;
}

/* Status Badges */
.badge-clean {
    background-color: rgba(53, 201, 143, 0.15);
    color: #35C98F;
    border: 1px solid rgba(53, 201, 143, 0.35);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
}

.badge-warning {
    background-color: rgba(243, 187, 87, 0.15);
    color: #F3BB57;
    border: 1px solid rgba(243, 187, 87, 0.35);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
}

.badge-critical {
    background-color: rgba(240, 120, 133, 0.15);
    color: #F07885;
    border: 1px solid rgba(240, 120, 133, 0.35);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
}

.badge-format {
    background-color: rgba(139, 124, 255, 0.18);
    color: #8B7CFF;
    border: 1px solid rgba(139, 124, 255, 0.4);
    padding: 3px 10px;
    border-radius: 14px;
    font-size: 0.8rem;
    font-weight: 600;
}

.badge-sheet {
    background-color: rgba(77, 216, 199, 0.18);
    color: #4DD8C7;
    border: 1px solid rgba(77, 216, 199, 0.4);
    padding: 3px 10px;
    border-radius: 14px;
    font-size: 0.8rem;
    font-weight: 600;
}

/* Welcome Hero Box */
.hero-box {
    background: linear-gradient(135deg, #151824 0%, #1B2030 100%);
    border: 1px solid #292E3D;
    border-radius: 12px;
    padding: 32px 36px;
    margin-bottom: 24px;
}

.hero-title {
    font-size: 2.3rem;
    font-weight: 800;
    color: #F5F6FA;
    letter-spacing: -0.5px;
    margin-bottom: 6px;
}

.hero-subtitle {
    font-size: 1.15rem;
    color: #8B7CFF;
    font-weight: 600;
    margin-bottom: 12px;
}

.hero-desc {
    font-size: 0.95rem;
    color: #A3A9BA;
    line-height: 1.6;
    max-width: 820px;
}

/* Sidebar Branding */
.brand-mark {
    font-size: 1.45rem;
    font-weight: 800;
    color: #F5F6FA;
    letter-spacing: -0.5px;
}

.brand-accent {
    color: #8B7CFF;
}

.brand-tagline {
    font-size: 0.78rem;
    color: #A3A9BA;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: -2px;
}

/* Navigation category label */
.nav-category {
    font-size: 0.72rem;
    font-weight: 700;
    color: #8B7CFF;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 14px;
    margin-bottom: 4px;
}

/* Sidebar Container */
[data-testid="stSidebar"] {
    background-color: #10121A;
    border-right: 1px solid #292E3D;
}

/* DataFrame Styling */
div[data-testid="stDataFrame"] {
    border-radius: 8px;
    border: 1px solid #292E3D;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session_state() -> None:
    """Initialize persistent Analytix session keys."""
    if "df" not in st.session_state:
        st.session_state["df"] = None
    if "dataset_name" not in st.session_state:
        st.session_state["dataset_name"] = None
    if "dataset_format" not in st.session_state:
        st.session_state["dataset_format"] = "CSV"
    if "active_worksheet" not in st.session_state:
        st.session_state["active_worksheet"] = None
    if "excel_raw_bytes" not in st.session_state:
        st.session_state["excel_raw_bytes"] = None
    if "excel_metadata" not in st.session_state:
        st.session_state["excel_metadata"] = None
    if "load_warnings" not in st.session_state:
        st.session_state["load_warnings"] = []
    if "current_nav" not in st.session_state:
        st.session_state["current_nav"] = "Overview"


init_session_state()


def handle_csv_upload(file_input: Any) -> None:
    """Load a CSV file into session state."""
    try:
        res = load_csv_detailed(file_input)
        st.session_state["df"] = res.df
        st.session_state["dataset_name"] = res.metadata.filename
        st.session_state["dataset_format"] = "CSV"
        st.session_state["active_worksheet"] = None
        st.session_state["excel_raw_bytes"] = None
        st.session_state["excel_metadata"] = None
        st.session_state["load_warnings"] = res.metadata.warnings
        st.toast(f"Loaded '{res.metadata.filename}' successfully!", icon="✅")
    except CSVEmptyError as e:
        st.error(f"⚠️ Empty CSV: {str(e)}")
    except CSVSizeLimitExceededError as e:
        st.error(f"⛔ File Size Limit Exceeded: {str(e)}")
    except CSVParsingError as e:
        st.error(f"❌ CSV Parsing Error: {str(e)}")
    except CSVEncodingError as e:
        st.error(f"🔤 CSV Encoding Error: {str(e)}")
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")


def handle_excel_upload(file_input: Any, sheet_name: Optional[str] = None, header_row: int = 0) -> None:
    """Inspect and load an Excel workbook into session state."""
    try:
        # Cache raw bytes for fast worksheet switching without re-uploading
        if hasattr(file_input, "read"):
            raw_bytes = file_input.read()
            if hasattr(file_input, "seek"):
                file_input.seek(0)
            st.session_state["excel_raw_bytes"] = raw_bytes
            wb_meta = inspect_excel_workbook(raw_bytes, filename=getattr(file_input, "name", "workbook.xlsx"))
        elif isinstance(file_input, (str, Path)):
            wb_meta = inspect_excel_workbook(file_input)
            st.session_state["excel_raw_bytes"] = Path(file_input).read_bytes()
        else:
            wb_meta = inspect_excel_workbook(file_input)

        st.session_state["excel_metadata"] = wb_meta
        st.session_state["dataset_name"] = wb_meta.filename
        st.session_state["dataset_format"] = f"Excel ({wb_meta.file_format})"

        target_sheet = sheet_name if sheet_name else wb_meta.sheet_names[0]
        res = load_excel_sheet(
            st.session_state["excel_raw_bytes"],
            sheet_name=target_sheet,
            header_row=header_row,
        )

        st.session_state["df"] = res.df
        st.session_state["active_worksheet"] = target_sheet
        st.session_state["load_warnings"] = res.metadata.warnings
        st.toast(f"Loaded Excel sheet '{target_sheet}' from '{wb_meta.filename}'!", icon="📊")

    except ExcelUnsupportedFormatError as e:
        st.error(f"⚠️ Unsupported Format: {str(e)}")
    except ExcelCorruptedError as e:
        st.error(f"❌ Corrupted Workbook: {str(e)}")
    except ExcelEmptyWorkbookError as e:
        st.error(f"⚠️ Empty Workbook: {str(e)}")
    except ExcelEmptySheetError as e:
        st.error(f"⚠️ Empty Worksheet: {str(e)}")
    except ExcelSheetNotFoundError as e:
        st.error(f"❌ Sheet Not Found: {str(e)}")
    except CSVSizeLimitExceededError as e:
        st.error(f"⛔ File Size Limit Exceeded: {str(e)}")
    except Exception as e:
        st.error(f"Error loading Excel workbook: {str(e)}")


def switch_excel_sheet(target_sheet: str, header_row: int = 0) -> None:
    """Switch active worksheet from the currently loaded workbook buffer."""
    if st.session_state["excel_raw_bytes"] is None:
        st.error("No Excel workbook buffer found in session.")
        return
    try:
        res = load_excel_sheet(
            st.session_state["excel_raw_bytes"],
            sheet_name=target_sheet,
            header_row=header_row,
        )
        st.session_state["df"] = res.df
        st.session_state["active_worksheet"] = target_sheet
        st.session_state["load_warnings"] = res.metadata.warnings
        st.toast(f"Switched to worksheet '{target_sheet}'!", icon="🔄")
    except Exception as e:
        st.error(f"Error switching to worksheet '{target_sheet}': {str(e)}")


def load_sample_csv() -> None:
    """Load the built-in sample Superstore CSV."""
    if SAMPLE_CSV_PATH.exists():
        handle_csv_upload(SAMPLE_CSV_PATH)
    else:
        st.error("Sample CSV file not found on disk.")


def load_sample_excel() -> None:
    """Load the built-in multi-sheet sample Excel workbook."""
    if SAMPLE_EXCEL_PATH.exists():
        handle_excel_upload(SAMPLE_EXCEL_PATH, sheet_name="Orders_Data")
    else:
        st.error("Sample Excel workbook not found on disk.")


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    # Sleek geometric logo & branding
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 2px;">
            <span style="font-size: 1.7rem; color: #8B7CFF;">◈</span>
            <span class="brand-mark">Analytix</span>
        </div>
        <div class="brand-tagline">Explore data. Discover insights.</div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    # Active dataset status widget
    if st.session_state["df"] is not None:
        df_active = st.session_state["df"]
        fmt_badge = (
            f'<span class="badge-format">{st.session_state["dataset_format"]}</span>'
        )
        st.markdown(
            f"**File**: `{st.session_state['dataset_name']}` {fmt_badge}",
            unsafe_allow_html=True,
        )

        if st.session_state["active_worksheet"]:
            sheet_badge = (
                f'<span class="badge-sheet">Sheet: {st.session_state["active_worksheet"]}</span>'
            )
            st.markdown(f"{sheet_badge}", unsafe_allow_html=True)

        st.caption(f"{len(df_active):,} rows × {len(df_active.columns):,} columns")

        # Fast sheet switcher in sidebar if an Excel workbook is active
        if (
            st.session_state["excel_metadata"] is not None
            and st.session_state["excel_metadata"].total_sheets > 1
        ):
            wb_meta: WorkbookMetadata = st.session_state["excel_metadata"]
            cur_idx = (
                wb_meta.sheet_names.index(st.session_state["active_worksheet"])
                if st.session_state["active_worksheet"] in wb_meta.sheet_names
                else 0
            )
            new_sheet = st.selectbox(
                "Active Sheet",
                options=wb_meta.sheet_names,
                index=cur_idx,
                key="sidebar_sheet_select",
            )
            if new_sheet != st.session_state["active_worksheet"]:
                switch_excel_sheet(new_sheet)
                st.rerun()

        if st.session_state["load_warnings"]:
            with st.expander("⚠️ Ingestion Notices", expanded=False):
                for w in st.session_state["load_warnings"]:
                    st.caption(f"• {w}")

        st.divider()

        # Categorized Navigation
        st.markdown('<div class="nav-category">WORKSPACE</div>', unsafe_allow_html=True)
        nav_workspace = ["Overview"]

        st.markdown('<div class="nav-category">EXPLORE</div>', unsafe_allow_html=True)
        nav_explore = ["Data Explorer", "Excel Explorer", "Data Preview"]

        st.markdown('<div class="nav-category">ANALYZE</div>', unsafe_allow_html=True)
        nav_analyze = ["Data Quality", "Statistics", "Visualizations", "Outlier Analysis"]

        st.markdown('<div class="nav-category">EXPORT</div>', unsafe_allow_html=True)
        nav_export = ["Export Reports"]

        all_nav_items = nav_workspace + nav_explore + nav_analyze + nav_export

        current_idx = (
            all_nav_items.index(st.session_state["current_nav"])
            if st.session_state["current_nav"] in all_nav_items
            else 0
        )
        selected_nav = st.radio(
            "Navigation Menu",
            options=all_nav_items,
            index=current_idx,
            label_visibility="collapsed",
        )
        st.session_state["current_nav"] = selected_nav

        st.divider()

        # Dataset Management Actions
        st.markdown("#### Manage Dataset")
        replace_file = st.file_uploader(
            "Upload new dataset",
            type=["csv", "xlsx", "xls"],
            key="sidebar_replace_uploader",
            label_visibility="collapsed",
        )
        if replace_file is not None:
            if replace_file.name != st.session_state["dataset_name"]:
                fn_lower = replace_file.name.lower()
                if fn_lower.endswith(".csv"):
                    handle_csv_upload(replace_file)
                else:
                    handle_excel_upload(replace_file)
                st.rerun()

        col_clr1, col_clr2 = st.columns(2)
        with col_clr1:
            if st.button("🔄 Samples", use_container_width=True, help="Reload sample dataset"):
                if "Excel" in st.session_state["dataset_format"]:
                    load_sample_excel()
                else:
                    load_sample_csv()
                st.rerun()
        with col_clr2:
            if st.button("🗑️ Clear", use_container_width=True, help="Clear active dataset"):
                st.session_state["df"] = None
                st.session_state["dataset_name"] = None
                st.session_state["active_worksheet"] = None
                st.session_state["excel_raw_bytes"] = None
                st.session_state["excel_metadata"] = None
                st.session_state["load_warnings"] = []
                st.session_state["current_nav"] = "Overview"
                st.rerun()

    else:
        st.info("No dataset loaded. Upload a CSV or Excel file, or launch a built-in sample dataset.")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("📄 Sample CSV", use_container_width=True, type="primary"):
                load_sample_csv()
                st.rerun()
        with col_s2:
            if st.button("📊 Sample Excel", use_container_width=True):
                load_sample_excel()
                st.rerun()

    st.divider()

    # Privacy notice & footer
    st.markdown("#### 🔒 Privacy Notice")
    st.caption(
        "Your data is processed in memory by this application. "
        "Do not upload confidential, personal, or sensitive information. "
        "Uploaded data is not stored persistently by this application."
    )

    st.markdown("---")
    st.caption(f"Analytix v{APP_VERSION} • Built with Streamlit, pandas & Plotly")


# ============================================================
# MAIN CONTENT AREA
# ============================================================

df: pd.DataFrame | None = st.session_state["df"]

# ------------------------------------------------------------
# EMPTY STATE (WHEN NO DATASET LOADED)
# ------------------------------------------------------------
if df is None:
    st.markdown(
        f"""
        <div class="hero-box">
            <div class="hero-title">Welcome to {APP_TITLE}</div>
            <div class="hero-subtitle">{APP_TAGLINE}</div>
            <div class="hero-desc">
                Analytix helps you explore datasets, understand data quality,
                calculate statistics, visualize patterns, and inspect multi-sheet
                Excel workbooks through a simple interactive interface.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_up_csv, col_up_excel, col_samples = st.columns([3, 3, 3], gap="medium")

    with col_up_csv:
        st.markdown(
            """
            <div class="analytix-card">
                <div class="analytix-card-title">📄 CSV Data Explorer</div>
                <div class="analytix-card-subtitle">
                    Upload comma or delimiter-separated tabular files with automatic encoding detection.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_csv = st.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            key="home_csv_uploader",
            help="Files are analyzed in memory up to 100 MB.",
        )
        if uploaded_csv is not None:
            handle_csv_upload(uploaded_csv)
            st.rerun()

    with col_up_excel:
        st.markdown(
            """
            <div class="analytix-card">
                <div class="analytix-card-title">📊 Excel Explorer (.xlsx, .xls)</div>
                <div class="analytix-card-subtitle">
                    Upload modern or legacy Excel workbooks with multi-worksheet discovery.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_excel = st.file_uploader(
            "Choose an Excel file",
            type=["xlsx", "xls"],
            key="home_excel_uploader",
            help="Supports modern .xlsx and legacy .xls workbooks.",
        )
        if uploaded_excel is not None:
            handle_excel_upload(uploaded_excel)
            st.rerun()

    with col_samples:
        st.markdown(
            """
            <div class="analytix-card">
                <div class="analytix-card-title">⚡ Instant Sample Workbooks</div>
                <div class="analytix-card-subtitle">
                    Try all features immediately with curated offline datasets.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🚀 Load Multi-Sheet Excel (3 sheets)", use_container_width=True, type="primary"):
            load_sample_excel()
            st.rerun()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        if st.button("📄 Load Sample CSV (Superstore)", use_container_width=True):
            load_sample_csv()
            st.rerun()

    st.markdown("---")
    st.markdown("### 🛠️ Platform Capabilities")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            """
            **1. Multi-Sheet Excel Explorer**  
            Inspect workbook metadata, preview individual sheets, and analyze them through the complete EDA engine.
            """
        )
    with c2:
        st.markdown(
            """
            **2. Data Quality Diagnostics**  
            Automated auditing of missing values, exact duplicates, and constant zero-variance columns with heuristic health score.
            """
        )
    with c3:
        st.markdown(
            """
            **3. In-Depth Statistics**  
            Sample-based numeric descriptive statistics (mean, median, IQR, skewness) and categorical frequency distributions.
            """
        )
    with c4:
        st.markdown(
            """
            **4. Outliers & Reports**  
            Interquartile range mathematical outlier flags and one-click exports to CSV and consolidated JSON reports.
            """
        )

# ------------------------------------------------------------
# LOADED DATASET SECTIONS
# ------------------------------------------------------------
else:
    section = st.session_state["current_nav"]

    # ========================================================
    # SECTION: OVERVIEW
    # ========================================================
    if section == "Overview":
        st.subheader("📊 Dataset Overview")
        ds_info = f"`{st.session_state['dataset_name']}`"
        if st.session_state["active_worksheet"]:
            ds_info += f" • Sheet: **{st.session_state['active_worksheet']}**"
        st.caption(f"Structural and integrity overview of {ds_info}")

        overview = get_dataset_overview(df)

        # Primary Metric Cards
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Total Rows", f"{overview.total_rows:,}")
        m2.metric("Total Columns", f"{overview.total_columns:,}")
        m3.metric("Memory Usage", overview.memory_usage_formatted)
        m4.metric("Numeric Cols", len(overview.numeric_columns))
        m5.metric("Categorical Cols", len(overview.categorical_columns))
        m6.metric(
            "Missing Cells",
            f"{overview.missing_cells_pct:.1f}%",
            help=f"{overview.total_missing_cells:,} total null cells",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1], gap="medium")
        with col_left:
            st.markdown(
                """
                <div class="analytix-card">
                    <div class="analytix-card-title">🧩 Variable Type Breakdown</div>
                    <div class="analytix-card-subtitle">Automatic semantic classification of column types</div>
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
                <div class="analytix-card">
                    <div class="analytix-card-title">⚡ Integrity Summary</div>
                    <div class="analytix-card-subtitle">Key dimensions and integrity markers</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write(f"- **Total Data Cells**: {overview.total_cells:,}")
            st.write(f"- **Format**: {st.session_state['dataset_format']}")
            if st.session_state["active_worksheet"]:
                st.write(f"- **Active Worksheet**: `{st.session_state['active_worksheet']}`")
            st.write(f"- **Missing Value Cells**: {overview.total_missing_cells:,} ({overview.missing_cells_pct}%)")
            st.write(f"- **Duplicate Rows**: {overview.total_duplicate_rows:,} ({overview.duplicate_rows_pct}%)")
            st.write(
                f"- **Clean Unique Observations**: {overview.total_rows - overview.total_duplicate_rows:,}"
            )

        st.markdown("### 📋 Column Metadata & Inferred Types")
        meta_df = get_column_metadata(df)
        st.dataframe(meta_df, use_container_width=True, hide_index=True)

    # ========================================================
    # SECTION: EXCEL EXPLORER
    # ========================================================
    elif section == "Excel Explorer":
        st.subheader("📊 Excel Explorer")
        st.caption("Inspect multi-sheet Excel workbooks (.xlsx, .xls), switch worksheets, and explore contents.")

        if st.session_state["excel_metadata"] is not None:
            wb_meta: WorkbookMetadata = st.session_state["excel_metadata"]

            # Workbook Header Card
            st.markdown(
                f"""
                <div class="analytix-card">
                    <div class="analytix-card-title">📁 Workbook: {wb_meta.filename}</div>
                    <div class="analytix-card-subtitle">
                        Format: {wb_meta.file_format} &bull; Total Worksheets: {wb_meta.total_sheets} &bull; File Size: {wb_meta.file_size_bytes / 1024:.1f} KB
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Worksheet selection & configuration controls
            ctrl_c1, ctrl_c2, ctrl_c3 = st.columns([3, 2, 2])
            with ctrl_c1:
                cur_sheet = st.session_state["active_worksheet"] or wb_meta.sheet_names[0]
                sheet_idx = wb_meta.sheet_names.index(cur_sheet) if cur_sheet in wb_meta.sheet_names else 0
                selected_sheet = st.selectbox(
                    "Select Worksheet to Analyze",
                    options=wb_meta.sheet_names,
                    index=sheet_idx,
                    help="Switching worksheets updates analysis across all sections.",
                )
            with ctrl_c2:
                header_row_choice = st.number_input(
                    "Header Row Index",
                    min_value=0,
                    max_value=10,
                    value=0,
                    help="Row index containing column headers (0 is first row).",
                )
            with ctrl_c3:
                st.write("")
                st.write("")
                if st.button("Apply / Switch Sheet", type="primary", use_container_width=True):
                    switch_excel_sheet(selected_sheet, header_row=header_row_choice)
                    st.rerun()

            # Automatically switch if user changed dropdown
            if selected_sheet != st.session_state["active_worksheet"]:
                switch_excel_sheet(selected_sheet, header_row=header_row_choice)
                st.rerun()

            # Worksheet Summary Cards
            st.markdown("#### Available Worksheets")
            sheet_cols = st.columns(min(len(wb_meta.sheets), 4))
            for i, s in enumerate(wb_meta.sheets):
                with sheet_cols[i % len(sheet_cols)]:
                    active_style = (
                        "border-color: #8B7CFF; background-color: #1B2030;"
                        if s.name == st.session_state["active_worksheet"]
                        else ""
                    )
                    empty_indicator = " (Empty)" if s.is_empty else ""
                    st.markdown(
                        f"""
                        <div class="analytix-card" style="padding: 12px 16px; margin-bottom: 10px; {active_style}">
                            <strong>{s.name}{empty_indicator}</strong><br>
                            <span style="font-size: 0.8rem; color: #A3A9BA;">
                                ~{s.row_count} rows &bull; {s.col_count} cols
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.divider()

            # Selected Sheet Data Preview
            st.markdown(f"### 🔍 Previewing Worksheet: `{st.session_state['active_worksheet']}`")
            st.caption(f"Showing records for active sheet ({len(df):,} rows × {len(df.columns)} columns)")

            p_rows = st.slider("Preview Rows", min_value=5, max_value=50, value=10, step=5, key="excel_preview_slider")
            st.dataframe(df.head(p_rows), use_container_width=True)

        else:
            st.info("Currently loaded dataset is not an Excel workbook. Upload an Excel file below to explore.")
            new_excel = st.file_uploader(
                "Upload Excel Workbook (.xlsx, .xls)",
                type=["xlsx", "xls"],
                key="excel_page_uploader",
            )
            if new_excel is not None:
                handle_excel_upload(new_excel)
                st.rerun()

            if st.button("🚀 Load Sample Multi-Sheet Excel Workbook"):
                load_sample_excel()
                st.rerun()

    # ========================================================
    # SECTION: DATA EXPLORER
    # ========================================================
    elif section == "Data Explorer":
        st.subheader("📄 Data Explorer")
        st.caption("Inspect tabular dataset attributes, replace or upload new CSV datasets.")

        st.markdown(
            f"""
            <div class="analytix-card">
                <div class="analytix-card-title">Dataset: {st.session_state['dataset_name']}</div>
                <div class="analytix-card-subtitle">
                    Format: {st.session_state['dataset_format']} &bull; Dimensions: {len(df):,} rows × {len(df.columns)} columns
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.dataframe(df.head(15), use_container_width=True)

        st.markdown("#### Upload Alternate CSV Dataset")
        new_csv = st.file_uploader("Upload CSV", type=["csv"], key="csv_page_uploader")
        if new_csv is not None:
            handle_csv_upload(new_csv)
            st.rerun()

    # ========================================================
    # SECTION: DATA PREVIEW
    # ========================================================
    elif section == "Data Preview":
        st.subheader("🔍 Data Preview & Column Inspection")
        ds_label = f"`{st.session_state['dataset_name']}`"
        if st.session_state["active_worksheet"]:
            ds_label += f" ({st.session_state['active_worksheet']})"
        st.caption(f"Inspect raw records and field distributions in {ds_label}")

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
    # SECTION: DATA QUALITY
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

        # Status & Score Banner
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
                sev_color = (
                    "#35C98F"
                    if issue.severity == IssueSeverity.INFO
                    else ("#F3BB57" if issue.severity == IssueSeverity.WARNING else "#F07885")
                )
                st.markdown(
                    f"""
                    <div style="border-left: 4px solid {sev_color}; padding-left: 14px; margin-bottom: 12px; background: #151824; padding: 12px 16px; border-radius: 4px;">
                        <strong style="color: #F5F6FA;">{issue.title}</strong> [{issue.severity.value}]<br>
                        <span style="color: #A3A9BA; font-size: 0.9rem;">{issue.description}</span>
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
            table_to_show = (
                m_sum.detail_table
                if show_all_cols
                else m_sum.detail_table[m_sum.detail_table["Missing Count"] > 0]
            )
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
            st.caption("Notice: Analytix only audits duplicate rows. Your dataset has not been modified.")
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
    # SECTION: STATISTICS
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
            cat_cols = [
                c for c in df.columns
                if c not in get_numeric_columns(df) and not pd.api.types.is_bool_dtype(df[c])
            ]
            if not cat_cols:
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
    # SECTION: VISUALIZATIONS
    # ========================================================
    elif section == "Visualizations":
        st.subheader("📉 Interactive Visualizations")
        st.caption("Responsive Plotly charts rendered directly from your active dataset.")

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
                        f"💡 The box plot shows the median line, quartiles (Q1, Q3), "
                        f"spread whiskers, and potential outlier points in **{box_col}**."
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
                        "💡 **Mentor Note**: Correlation measures linear association between -1.0 (inverse) "
                        "and +1.0 (direct). Correlation does **not** imply causation!"
                    )
                else:
                    st.info("Select at least 2 columns to calculate correlation.")

    # ========================================================
    # SECTION: OUTLIER ANALYSIS
    # ========================================================
    elif section == "Outlier Analysis":
        st.subheader("🎯 Outlier Analysis (Interquartile Range Method)")
        st.caption("Mathematical IQR outlier detection identifying observations outside expected statistical spread.")

        with st.expander("📐 How the Interquartile Range (IQR) Rule Works", expanded=True):
            st.markdown(
                """
                1. **First Quartile (Q1)**: 25th percentile of valid observations.
                2. **Third Quartile (Q3)**: 75th percentile of valid observations.
                3. **IQR**: $\\text{IQR} = Q3 - Q1$.
                4. **Lower Bound**: $Q1 - (k \\times \\text{IQR})$.
                5. **Upper Bound**: $Q3 + (k \\times \\text{IQR})$ (where $k=1.5$ standard, $k=3.0$ extreme).

                Values falling strictly outside these boundaries are flagged as potential outliers.  
                *Important: Outliers are mathematical flags, not necessarily errors. They often highlight key business anomalies, high-value transactions, or rare system events.*
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
    # SECTION: EXPORT REPORTS
    # ========================================================
    elif section == "Export Reports":
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
                <div class="analytix-card">
                    <div class="analytix-card-title">📄 CSV Table Exports</div>
                    <div class="analytix-card-subtitle">Download clean tabular summaries for presentations or spreadsheets</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            file_prefix = st.session_state["dataset_name"].replace(".xlsx", "").replace(".csv", "").replace(".xls", "")
            if st.session_state["active_worksheet"]:
                file_prefix += f"_{st.session_state['active_worksheet']}"

            # 1. Dataset Overview / Metadata
            overview_csv = export_dataframe_to_csv(meta_df)
            st.download_button(
                "📥 Column Metadata & Overview (CSV)",
                data=overview_csv,
                file_name=f"{file_prefix}_column_metadata.csv",
                mime="text/csv",
                use_container_width=True,
            )

            # 2. Data Quality Table
            quality_csv = export_dataframe_to_csv(quality_report.missing_summary.detail_table)
            st.download_button(
                "📥 Missing Values Audit (CSV)",
                data=quality_csv,
                file_name=f"{file_prefix}_missing_values.csv",
                mime="text/csv",
                use_container_width=True,
            )

            # 3. Numeric Statistics Table
            if not num_stats_df.empty:
                stats_csv = export_dataframe_to_csv(num_stats_df)
                st.download_button(
                    "📥 Numeric Descriptive Statistics (CSV)",
                    data=stats_csv,
                    file_name=f"{file_prefix}_numeric_statistics.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            # 4. Duplicate Rows (if any)
            if quality_report.duplicate_summary.total_duplicates > 0:
                dup_csv = export_dataframe_to_csv(quality_report.duplicate_summary.duplicate_rows_preview)
                st.download_button(
                    "📥 Flagged Duplicate Rows (CSV)",
                    data=dup_csv,
                    file_name=f"{file_prefix}_duplicate_rows.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        with exp_col2:
            st.markdown(
                """
                <div class="analytix-card">
                    <div class="analytix-card-title">📦 Consolidated JSON EDA Report</div>
                    <div class="analytix-card-subtitle">
                        Comprehensive programmatic audit summary with format and worksheet metadata.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

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
                dataset_format=st.session_state["dataset_format"],
                active_worksheet=st.session_state["active_worksheet"],
            )

            st.download_button(
                "📥 Download Consolidated JSON Report",
                data=json_report_str.encode("utf-8"),
                file_name=f"{file_prefix}_eda_report.json",
                mime="application/json",
                type="primary",
                use_container_width=True,
            )

            with st.expander("👁️ Preview JSON Report Content", expanded=False):
                st.json(json_report_str)
