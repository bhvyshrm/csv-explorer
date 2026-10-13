# CSV Explorer 📊

> **"Understand your data before you build with it."**  
> An interactive, beginner-friendly, portfolio-quality Exploratory Data Analysis (EDA) web application built with Python, Streamlit, pandas, and Plotly.

---

## 📌 Problem Statement

Exploratory Data Analysis (EDA) is the essential first step in every data science and analytics lifecycle. However, writing custom boilerplate code for inspecting missing values, data distributions, duplicate records, correlation heatmaps, and outlier thresholds can be repetitive, error-prone, and intimidating for students, analysts, and beginners.

**CSV Explorer** solves this by providing a zero-code, instant profiling interface: upload any CSV file and immediately explore its structure, data quality health, descriptive statistics, interactive distributions, and outlier boundaries — with full privacy and in-memory execution.

---

## ✨ Key Features

- **⚡ Instant Dataset Profiling**: Ingests CSV files, reports total rows, columns, memory footprint, and automatically categorizes fields into numeric, categorical, datetime, and boolean types.
- **🛡️ Data Quality Diagnostic Audit**:
  - Null value detection with column-wise percentages and interactive missing-value horizontal bar charts.
  - Exact duplicate row auditing with side-by-side previews without altering underlying records.
  - Detection of constant (zero-variance) columns, entirely empty columns, and configurable nearly-empty columns (default 90% missing).
  - Transparent heuristic quality score (0–100) and explicit issue severity tags.
- **📈 Comprehensive Statistical Depth**:
  - Sample-based numeric descriptive statistics: count, missing count, mean, median, standard deviation ($ddof=1$), variance, min, max, Q1, Q3, IQR, and skewness.
  - Safe mathematical handling: undefined statistics preserve `NaN`/`None` rather than misrepresenting them as `0.0`.
  - Categorical frequency distribution tables with top-N filtering, omission warnings, and mode metrics.
- **📉 Interactive Plotly Visualizations**:
  - Dynamic histograms with configurable binning and mean/median reference lines.
  - Box plots with quartile whiskers and interactive outlier point inspection.
  - Categorical bar charts sorted descending with percentage contribution markers.
  - Diverging correlation heatmaps (Pearson and Spearman methods) with automatic low-variance safeguards.
- **🎯 Mathematical Outlier Detection (IQR Method)**:
  - Interquartile Range evaluation ($Q1 - 1.5 \times IQR$ to $Q3 + 1.5 \times IQR$).
  - Configurable multiplier ($1.5\times$ for standard, $3.0\times$ for extreme outliers).
  - Preview and direct CSV export of flagged outlier records.
- **💾 Comprehensive Report Exports**:
  - Download individual tables (column metadata, data quality audit, numeric statistics, category frequencies, flagged outliers) as CSV.
  - Download a consolidated, JSON-safe programmatic EDA report.
- **🔒 In-Memory Privacy & Security**:
  - No database, no third-party tracking, and no external AI API data transmission.

---

## 🧰 Technology Stack

- **Language**: Python 3.11+ (tested on Python 3.11 – 3.14)
- **Web Application Framework**: [Streamlit](https://streamlit.io/)
- **Data Manipulation & Computation**: [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Interactive Visualizations**: [Plotly](https://plotly.com/python/) (Plotly Graph Objects & Plotly Express)
- **Testing & Quality Assurance**: [pytest](https://pytest.org/)

---

## 🖼️ Application Interface & Screenshots

> *Placeholder: Add screenshots or GIFs of your local application running here.*

```
+------------------------------------------------------------------------------------+
| 📊 CSV Explorer               Dataset: sample_superstore_eda.csv (122 × 16)        |
+------------------------------------------------------------------------------------+
| [Overview]    [Data Preview]   [Data Quality]   [Statistics]   [Visualizations]... |
|                                                                                    |
| [122 Rows]   [16 Columns]   [18.4 KB Memory]   [5 Numeric]   [1.8% Missing Cells]  |
|                                                                                    |
|  +---------------------------+   +----------------------------------------------+  |
|  | Missing Values Chart      |   | Interactive Sales Histogram                  |  |
|  | ========================= |   |       _/\_                                   |  |
|  | Discount:  5.0%           |   |      /    \  | Mean: $248.50                 |  |
|  | Region:    4.9%           |   | ____/      \_|________________               |  |
|  +---------------------------+   +----------------------------------------------+  |
+------------------------------------------------------------------------------------+
```

---

## 🏗️ Architecture & Design Philosophy

The application strictly separates analytical computation from the user interface:

```
csv-explorer/
│
├── app.py                     # Streamlit frontend shell, state management & UI routing
├── requirements.txt           # Production & development dependencies
├── README.md                  # Complete project documentation
├── .gitignore                 # Standard Python, venv, and OS ignore rules
│
├── .streamlit/
│   └── config.toml            # Dark SaaS theme palette & server parameters
│
├── src/                       # Core analytical engine (100% independently testable)
│   ├── __init__.py            # Package root & semantic version
│   ├── data_loader.py         # CSV ingestion, encoding fallback & size validation
│   ├── data_overview.py       # Structural dimensions, types, & column metadata
│   ├── data_quality.py        # Nulls, duplicates, constant & sparse columns audit
│   ├── statistics.py          # Numeric descriptive statistics & categorical mode
│   ├── visualizations.py      # Plotly interactive dark charts & heatmaps
│   ├── outliers.py            # IQR mathematical outlier detection
│   └── export.py              # Clean CSV bytes & JSON-safe report assembling
│
├── tests/                     # Automated pytest test suite
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_data_overview.py
│   ├── test_data_quality.py
│   ├── test_statistics.py
│   ├── test_visualizations.py
│   ├── test_outliers.py
│   ├── test_export.py
│   └── test_integration_pipeline.py
│
└── sample_data/
    ├── README.md              # Documentation of sample dataset fields & test cases
    └── sample_superstore_eda.csv  # 122-row multi-attribute retail test dataset
```

---

## 🚀 Getting Started Locally

### 1. Prerequisites

Ensure you have **Python 3.11** or a later supported version installed. Verify via:

```bash
python3 --version
```

### 2. Clone the Repository

```bash
git clone <your-repository-url>
cd "CSV Explorer"
```

### 3. Create and Activate a Virtual Environment

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows (Command Prompt / PowerShell):**
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

The application will start locally at `http://localhost:8501`.

---

## 🧪 Running the Test Suite

Run the full automated test suite with pytest:

```bash
python -m pytest tests/ -v
```

To run tests with concise output:

```bash
python -m pytest tests/ -q
```

All 40 unit and integration tests execute independently without requiring an active Streamlit server or browser.

---

## 📐 Methodology & Statistical Rules

### 1. Inferred Data Types
- **Boolean**: Strictly checked first to avoid NumPy's boolean subclassing under integers.
- **Datetime**: Evaluated via pandas datetime dtypes.
- **Numeric**: Standard floating point and integer types.
- **Categorical**: String, text objects, and categorical types.

### 2. Missing Values & Low Variance
- Missing cells are computed with `isna()`.
- Constant columns are defined as having strictly 1 distinct non-null value (`series.dropna().nunique() == 1`).
- Completely empty columns (0 non-null values) are distinguished from constant columns.
- Nearly empty columns are flagged when null percentage exceeds the user-configured threshold (default $90\%$).

### 3. Interquartile Range (IQR) Outlier Rule
For any numeric column:
1. $Q1 = 25\text{th percentile of valid observations}$
2. $Q3 = 75\text{th percentile of valid observations}$
3. $\text{IQR} = Q3 - Q1$
4. $\text{Lower Bound} = Q1 - (k \times \text{IQR})$
5. $\text{Upper Bound} = Q3 + (k \times \text{IQR})$ (where $k = 1.5$ standard, or $k = 3.0$ extreme)
6. Flagged if: $\text{value} < \text{Lower Bound} \lor \text{value} > \text{Upper Bound}$

> **Mentor Note**: Outliers are statistical flags, not necessarily errors. Never automatically delete or cap outliers without contextual domain investigation.

---

## 🔒 Privacy & Limitations

- **File Size Limit**: Configured to 100 MB by default to prevent browser memory exhaustion.
- **In-Memory Analysis**: Datasets are processed purely in Python memory. They are not persisted to a database or sent to external cloud APIs.
- **Do Not Upload Confidential Information**: While data is processed locally in memory, users should refrain from uploading sensitive, personal, or confidential information.
- **Known Limitations**: Large files ($> 100\text{ MB}$) with millions of rows may experience slower rendering in the browser; use column subsampling or filtering prior to uploading large Big Data files.

---

## ☁️ Deployment Instructions (Streamlit Community Cloud)

1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "feat: complete CSV Explorer implementation"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```
2. Visit [share.streamlit.io](https://share.streamlit.io/).
3. Connect your GitHub account and select your repository.
4. Set `app.py` as the Main file path.
5. Click **Deploy**.

---

## 🗺️ Future Roadmap

- [ ] Automated column type coercion recommendations (e.g. string to datetime or categorical)
- [ ] Bivariate scatter plots with regression trend lines
- [ ] Exportable PDF executive summary reports
- [ ] Synthetic data generation based on discovered distributions

---

## 📄 License

Distributed under the MIT License. Feel free to use this project for your portfolio, learning, or data exploration work.
