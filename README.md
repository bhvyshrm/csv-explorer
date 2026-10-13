# Analytix 2.0 ◈

> **"Explore data. Discover insights."**  
> A modern, multi-format exploratory data analysis platform built with Python, Streamlit, pandas, and Plotly.

---

## 📌 Product Overview

**Analytix** is a multi-format exploratory data analysis (EDA) and profiling application designed for analysts, data scientists, students, and engineers.

Whether working with standard comma-separated files (`.csv`) or multi-worksheet modern and legacy spreadsheets (`.xlsx`, `.xls`), Analytix offers instant in-memory dataset profiling, automated data quality health auditing, robust descriptive statistics, interactive dark-themed Plotly charts, and mathematical outlier detection — with zero code required and complete local privacy.

---

## ✨ Key Features

### 📊 1. Multi-Sheet Excel Explorer *(New in 2.0)*
- **Workbook Metadata Inspection**: Discovers worksheet names, dimensions (rows $\times$ columns), and detects blank or template worksheets.
- **Interactive Worksheet Selection**: Seamlessly switch between sheets in a single workbook without re-uploading; automatically refreshes the entire analysis engine.
- **Format Compatibility**: Modern `.xlsx` workbooks (via `openpyxl`) and legacy `.xls` sheets (via `xlrd`).
- **Data Fidelity**: Preserves dates, numerics, and strings while reading evaluated formula outputs and handling merged cells gracefully.

### 📄 2. Resilient CSV Ingestion
- Automatic fallback decoding across UTF-8, UTF-8 BOM (`utf-8-sig`), Latin-1 (`iso-8859-1`), and CP1252.
- Handles empty files, header-only datasets, whitespace files, and duplicate column headers safely.
- Configurable file-size safeguard (default 100 MB).

### 🛡️ 3. Data Quality Diagnostic Audit
- **Missing Value Analysis**: Column-level null counts and percentages paired with interactive horizontal bar charts.
- **Duplicate Row Detection**: Live side-by-side inspection of duplicate rows without altering underlying data.
- **Variance Diagnostics**: Identifies constant (zero-variance) columns, entirely empty columns, and configurable nearly-empty columns (default $\ge 90\%$ missing).
- **Heuristic Health Score**: Transparent 0–100 data health rating with explicit `INFO`, `WARNING`, and `CRITICAL` diagnostic tags.

### 📈 4. Comprehensive Statistical Depth
- **Numeric Descriptive Metrics**: Valid counts, missing counts, mean, median, sample standard deviation ($ddof=1$), sample variance, min, max, Q1 (25%), Q3 (75%), IQR, and skewness. Undefined statistics preserve `NaN`/`None` rather than being converted to misleading zeros.
- **Categorical Frequency Tables**: Cardinality counts, mode (most frequent category), frequency distributions, and configurable top-$N$ filtering with omission counters.
- **Built-in Mentorship**: Beginner-friendly explanations of statistical metrics (mean vs. median, IQR, spread, skewness).

### 📉 5. Interactive Visualizations
- **Distributions**: Dynamic histograms with configurable bin counts and dashed mean/median indicators.
- **Spread & Quartiles**: Interactive box plots with quartile whiskers and outlier point toggles.
- **Categorical Breakdown**: Sorted frequency bar charts with percentage contribution annotations.
- **Correlations**: Diverging heatmaps supporting Pearson and Spearman correlation coefficients with automatic safeguards for low-variance columns.

### 🎯 6. Mathematical Outlier Detection (IQR Rule)
- Implements the standard Interquartile Range boundary formula: $[\text{Q1} - k \times \text{IQR},\, \text{Q3} + k \times \text{IQR}]$.
- Adjustable multiplier slider ($1.5\times$ for standard outliers, $3.0\times$ for extreme outliers).
- Live preview and direct CSV export of flagged outlier records.

### 💾 7. Export & Reporting
- Download individual tabular summaries (metadata, missing values, statistics, categorical frequencies, flagged outliers) as CSV.
- Download a consolidated, JSON-safe programmatic EDA report including source filename, format, and active worksheet metadata.

### 🔒 8. In-Memory Privacy & Security
- 100% in-memory processing. Datasets are never persisted to a database, tracked, or transmitted to third-party AI APIs.

---

## 🧰 Technology Stack

- **Core Language**: Python 3.11+ (tested on Python 3.11 – 3.14)
- **Application Framework**: [Streamlit](https://streamlit.io/)
- **Data Processing**: [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Excel Ingestion**: [openpyxl](https://openpyxl.readthedocs.io/) (`.xlsx`), [xlrd](https://xlrd.readthedocs.io/) (`.xls`)
- **Interactive Visualizations**: [Plotly](https://plotly.com/python/) (Graph Objects & Express)
- **Testing & Verification**: [pytest](https://pytest.org/)

---

## 🖼️ Application Interface & Layout

```
+----------------------------------------------------------------------------------------+
| ◈ Analytix               File: sample_analytix_multisheet.xlsx  [Excel (.xlsx)]        |
| Explore data. Insights.  Active Sheet: Orders_Data (101 rows × 8 cols)                 |
+----------------------------------------------------------------------------------------+
| WORKSPACE                [101 Rows]   [8 Columns]   [14.2 KB Memory]   [3 Numeric]     |
| • Overview                                                                             |
| EXPLORE                  +-----------------------------+ +---------------------------+ |
| • Data Explorer          | Missing Values Chart        | | Sales Distribution        | |
| • Excel Explorer         | =========================== | |       _/\_                | |
| • Data Preview           | Profit: 3.0% (3 nulls)      | |      /    \  Mean: $286.40| |
| ANALYZE                  | Region: 5.0% (5 nulls)      | | ____/      \_|____________| |
| • Data Quality           +-----------------------------+ +---------------------------+ |
| • Statistics                                                                           |
| • Visualizations         +-----------------------------------------------------------+ |
| • Outlier Analysis       | Active Sheet Selector: [ Orders_Data             v ]      | |
| EXPORT                   | Available: Orders_Data (101) | Customer_Demographics (50) | |
| • Export Reports         +-----------------------------------------------------------+ |
+----------------------------------------------------------------------------------------+
```

---

## 🏗️ Architecture & Project Structure

Analytix strictly isolates data transformation and analytical computation inside `src/` to guarantee independent automated testability without requiring a web browser or Streamlit runtime.

```
CSV Explorer/
├── .gitignore                     # Git ignore rules for Python, venv, and caches
├── .streamlit/
│   └── config.toml                # Analytix 2.0 dark SaaS theme configuration
├── README.md                      # Comprehensive platform documentation
├── app.py                         # Streamlit frontend, state routing & UI shell
├── requirements.txt               # Dependencies with version constraints
│
├── sample_data/
│   ├── README.md                  # Documentation of test cases and sample fields
│   ├── sample_superstore_eda.csv  # 122-row retail CSV dataset with intentional anomalies
│   └── sample_analytix_multisheet.xlsx # 3-sheet Excel workbook (.xlsx)
│
├── src/                           # Analytical engine (100% unit-testable)
│   ├── __init__.py                # Package version marker (v2.0.0)
│   ├── data_loader.py             # CSV loading, encoding fallbacks, and validation
│   ├── excel_loader.py            # Excel inspection, multi-sheet discovery & parsing
│   ├── data_overview.py           # Dimensions, memory, and semantic type classification
│   ├── data_quality.py            # Nulls, duplicates, constant, and sparse column audit
│   ├── statistics.py              # Numeric descriptive statistics & categorical mode
│   ├── visualizations.py          # Dark SaaS Plotly charts and correlation heatmaps
│   ├── outliers.py                # IQR mathematical outlier detection
│   └── export.py                  # CSV bytes & JSON-safe report assembling
│
└── tests/                         # Automated pytest test suite
    ├── __init__.py
    ├── test_data_loader.py        # 11 CSV ingestion tests
    ├── test_excel_loader.py       # 12 Excel inspection and sheet tests
    ├── test_data_overview.py      # 5 structural overview tests
    ├── test_data_quality.py       # 5 quality audit tests
    ├── test_statistics.py         # 5 descriptive statistics tests
    ├── test_visualizations.py     # 6 Plotly visualization tests
    ├── test_outliers.py           # 4 IQR outlier tests
    ├── test_export.py             # 3 CSV & JSON serialization tests
    └── test_integration_pipeline.py # End-to-end integration test
```

---

## 🚀 Getting Started Locally

### 1. Prerequisites
Ensure you have **Python 3.11** or a later supported version installed:
```bash
python3 --version
```

### 2. Clone the Repository
```bash
git clone https://github.com/bhvyshrm/csv-explorer.git
cd "CSV Explorer"
```

### 3. Virtual Environment Setup

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows (PowerShell / Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 4. Install Dependencies
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Launch the Application
```bash
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📊 Excel Explorer Workflow

1. **Upload Workbook**: Drag and drop any `.xlsx` or `.xls` file onto the upload area, or click **Sample Excel** to load the built-in 3-sheet workbook.
2. **Inspect Sheet Metadata**: Analytix reads all sheet names, estimated row counts, column counts, and sample headers.
3. **Select Active Worksheet**: Use the worksheet dropdown to choose a sheet. The application automatically normalizes the sheet into pandas and immediately updates the active dataset.
4. **Explore Across Sections**:
   - **Overview**: View sheet dimensions and inferred data types.
   - **Data Quality**: Audit nulls, duplicates, and constant fields.
   - **Statistics**: Review numeric metrics (mean, median, IQR, skewness) and category frequencies.
   - **Visualizations**: Render interactive histograms, box plots, bar charts, and correlation heatmaps.
   - **Outliers**: Inspect IQR boundaries and preview flagged records.
   - **Export Reports**: Download CSV summaries or a consolidated JSON audit tagged with the active worksheet name.

---

## 🧪 Running the Test Suite

Run all automated unit and integration tests with pytest:

```bash
python -m pytest tests/ -v
```

For concise test output:

```bash
python -m pytest tests/ -q
```

All 52 tests run locally in under 1 second without requiring an external internet connection, database, or browser.

---

## 📐 Methodology & Statistical Rules

### 1. Inferred Data Types
- **Boolean**: Checked first to prevent NumPy boolean subclassing errors.
- **Datetime**: Evaluated via pandas datetime dtypes and Excel date formats.
- **Numeric**: Standard floating point and integer types.
- **Categorical**: String, text objects, and categorical types.

### 2. Data Quality Health Score Heuristic
A transparent 0–100 score computed via explicit penalties:
- Base score = $100$
- Missing values: $-1$ point per $2\%$ missing cells (up to $-30$)
- Duplicate rows: $-1$ point per $2\%$ duplicate rows (up to $-25$)
- Constant columns: $-5$ points per constant column (up to $-15$)
- Nearly empty columns ($\ge 90\%$ missing): $-10$ points per column (up to $-20$)
- Entirely empty columns: $-15$ points per column (up to $-30$)

Status rating:
- $\ge 85$: *"No major issues detected"*
- $65 - 84$: *"Some issues need attention"*
- $< 65$: *"Several data quality issues detected"*

### 3. Interquartile Range (IQR) Outlier Rule
1. $\text{Q1} = 25\text{th percentile of valid observations}$
2. $\text{Q3} = 75\text{th percentile of valid observations}$
3. $\text{IQR} = \text{Q3} - \text{Q1}$
4. $\text{Lower Bound} = \text{Q1} - (k \times \text{IQR})$
5. $\text{Upper Bound} = \text{Q3} + (k \times \text{IQR})$ (where $k=1.5$ standard, $k=3.0$ extreme)
6. Flagged if: $\text{value} < \text{Lower Bound} \lor \text{value} > \text{Upper Bound}$

---

## 🔒 Privacy & Limitations

- **File Size Cap**: Configured to 100 MB by default to prevent client browser memory exhaustion.
- **In-Memory Analysis**: Datasets are analyzed in volatile memory and are not stored in a persistent database or transmitted to external servers.
- **Formulas**: In `.xlsx` workbooks, cached evaluated formula values are read (`data_only=True`). Formula recalculation engines are not executed in memory.
- **Privacy Notice**: Users should avoid uploading sensitive, confidential, or regulated private data.

---

## ☁️ Deployment Instructions (Streamlit Community Cloud)

1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "feat: upgrade to Analytix 2.0 with Excel Explorer"
   git push origin main
   ```
2. Navigate to [share.streamlit.io](https://share.streamlit.io/).
3. Connect your GitHub account and select your repository.
4. Set `app.py` as the entrypoint file.
5. Click **Deploy**.

---

## 📄 License

Distributed under the MIT License. Built for portfolio presentation, open learning, and zero-code exploratory data analysis.
