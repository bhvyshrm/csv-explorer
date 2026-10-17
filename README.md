# Analytix ◈

> **Explore data. Discover insights.**  
> *Powerful data exploration and reporting, free to use.*

[![CI Tests](https://img.shields.io/badge/pytest-100%20passed-emerald.svg)](tests/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Serverless-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📌 Product Overview

**Analytix** is an accessible, free-to-use data exploration and reporting platform that empowers students, analysts, researchers, data scientists, and engineers to upload files, profile datasets, analyze data quality, discover patterns, generate interactive visualizations, and download publication-ready reports — without writing a single line of code.

Built with a high-performance **Next.js 14 frontend** featuring a modern glassmorphic interface inspired by contemporary SaaS design, paired with a robust **FastAPI serverless backend** and Python data science engine (`pandas`, `numpy`, `openpyxl`, `plotly`, `pyarrow`).

---

## ✨ Key Capabilities

### 🗂️ 1. Multi-Format Data Explorer
Analytix implements modular, isolated parsing pipelines for every supported format:

- **CSV Explorer (`.csv`)**: Intelligent delimiter inference (comma, semicolon, tab), automatic encoding fallback (`utf-8`, `utf-8-sig`, `latin1`, `cp1252`), whitespace normalization, and duplicate header disambiguation.
- **Excel Explorer (`.xlsx`, `.xls`)**: Multi-sheet workbook metadata inspection, active worksheet switching without re-uploading, evaluated formula preservation (`openpyxl`), and legacy spreadsheet support (`xlrd`).
- **JSON Explorer (`.json`, `.ndjson`, `.jsonl`)**: Ingestion of standard record arrays, root container key unwrapping (`data`, `records`, `items`), and automated nested dictionary flattening using dot notation (`user.address.city`). Line-by-line validation and corrupted-line diagnostics for newline-delimited JSON.
- **Parquet Explorer (`.parquet`)**: High-performance Apache Parquet columnar reader powered by PyArrow, supporting schema introspection, dimensions, and typed analytics.
- **TSV Explorer (`.tsv`, `.tab`)**: Dedicated tab-separated value parsing with encoding fallbacks and header validation.
- **Text & Log Explorer (`.txt`, `.log`)**: Line counts, character counts, blank-line distributions, and structured pattern recognition (ISO timestamps, log levels `INFO`/`WARN`/`ERROR`, and Apache/Nginx web access logs).
- **XML Explorer (`.xml`)**: Secure XML ingestion hardened against XML External Entity (XXE) and entity expansion attacks, automatically converting repeating element tags and attributes into tabular records.
- **Database Explorer**: Planned connection interface for PostgreSQL, MySQL, and SQLite (honest status: *Coming soon*).

---

### 🛡️ 2. Data Quality & Health Audit
- **Heuristic Health Score (0–100)**: Instant data health score with categorized diagnostic tags (`INFO`, `WARNING`, `CRITICAL`).
- **Missing Value Analysis**: Column-level null counts and percentages paired with missing value charts.
- **Duplicate Row Detection**: Live side-by-side inspection of duplicate rows without mutating underlying data.
- **Variance Diagnostics**: Automatic identification of constant (zero-variance) columns, entirely empty columns, and nearly-empty columns ($\ge 90\%$ missing).

---

### 📈 3. Comprehensive Descriptive Statistics
- **Numeric Metrics**: Mean, median, sample standard deviation ($ddof=1$), quartiles (Q1, Q3), Interquartile Range (IQR), minimum, maximum, variance, and skewness.
- **Categorical Distributions**: Unique value counts (cardinality), most frequent mode, and frequency tables.
- **Beginner-Friendly Mentorship**: Built-in contextual guidance explaining statistical concepts directly in the workspace.

---

### 🎯 4. Outlier Analysis & Correlations
- **Mathematical Outlier Detection (Tukey's IQR Rule)**: Configurable outlier threshold $[\text{Q1} - k \times \text{IQR},\, \text{Q3} + k \times \text{IQR}]$ with interactive slider ($1.0\times$ to $3.0\times$), lower/upper count breakdowns, and flagged row previews.
- **Correlation Engine**: Pairwise Pearson, Spearman, and Kendall correlation matrices with interactive heatmaps and column multi-selection.

---

### 📉 5. Interactive Visualizations
- Interactive, responsive Plotly charts:
  - Histograms with dynamic bin count sliders
  - Box plots with quartile whiskers and outlier points
  - Categorical frequency bar charts
  - Correlation heatmaps
  - Missing value distribution charts

---

### 📥 6. Professional Report Center
Generate and download complete analytical outputs with one click:
1. **Complete Analysis Report (`.ZIP`)**: Comprehensive archive containing:
   - `summary_report.html`: Standalone, print/PDF-ready executive analysis summary
   - `analysis_workbook.xlsx`: Styled multi-sheet Excel workbook
   - `eda_report.json`: Machine-readable structured audit data
   - Modular CSVs: `column_metadata.csv`, `missing_values.csv`, `numeric_statistics.csv`, `correlation_matrix.csv`, `outliers_report.csv`, and `sample_preview.csv`
   - `README.txt`: Explaining all generated files and metadata
2. **Analysis Workbook (`.XLSX`)**: Multi-tab formatted spreadsheet generated via `openpyxl`.
3. **Executive Summary (`.HTML`)**: Clean, responsive executive report ready for presentation or printing to PDF.
4. **Structured JSON Report (`.JSON`)**: Programmatic EDA report with full metrics.
5. **Individual Modular CSVs**: Direct downloads for metadata, missing values, statistics, duplicates, and outliers.

---

## 🔒 Privacy, Security & Resource Limits

- **100% In-Memory Processing**: Uploaded files are processed in transient serverless memory and are never persisted to a database or permanent disk storage.
- **Zero Third-Party AI Data Sharing**: Raw datasets are never transmitted to external AI APIs or marketing trackers.
- **Vercel Serverless Upload Limit**: Enforces a strict 4.5 MB payload limit matching Vercel's serverless runtime constraints to ensure fast response times and avoid function timeouts.
- **Safe Parsing Guards**: XML parser strictly disables external entity expansion (`<!DOCTYPE`, `<!ENTITY`) to prevent XXE vulnerabilities.

---

## 🧰 Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | [Next.js 14](https://nextjs.org/) (App Router), [React 18](https://react.dev/), [TypeScript](https://www.typescriptlang.org/), [Tailwind CSS](https://tailwindcss.com/), [Lucide Icons](https://lucide.dev/), [Plotly.js](https://plotly.com/javascript/) |
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com/), [Pydantic v2](https://docs.pydantic.dev/), [Uvicorn](https://www.uvicorn.org/) |
| **Data Engine** | [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), [openpyxl](https://openpyxl.readthedocs.io/), [xlrd](https://xlrd.readthedocs.io/), [PyArrow](https://arrow.apache.org/docs/python/) |
| **Testing** | [pytest](https://pytest.org/) (100 unit & integration tests) |
| **Deployment** | [Vercel](https://vercel.com/) (Next.js Edge + Serverless Python Runtime) |

---

## 📁 Repository Structure

```
├── api/
│   └── index.py               # FastAPI serverless entrypoint & routing middleware
├── app/
│   ├── globals.css            # Glassmorphism utilities & pastel design tokens
│   ├── layout.tsx             # Root layout & Analytix metadata
│   └── page.tsx               # Master page controller (Landing & Workspace)
├── components/
│   ├── PlotlyChart.tsx        # Responsive Plotly chart wrapper with light/dark theme
│   ├── homepage/              # Glassmorphic homepage components
│   │   ├── Navbar.tsx         # Responsive navigation bar
│   │   ├── Hero.tsx           # Hero section with interactive preview
│   │   ├── QuickStartUpload.tsx # Drag & drop upload area + sample catalog
│   │   ├── FormatGrid.tsx     # 6 Format Explorer cards matching visual reference
│   │   ├── CapabilitiesGrid.tsx # What You Can Do capability matrix
│   │   ├── HowItWorks.tsx     # 3-step workflow guide
│   │   ├── AnalyticsPreview.tsx # Workflow demonstration
│   │   ├── PrivacyTrust.tsx   # Honest privacy & security breakdown
│   │   └── Footer.tsx         # Footer with final CTA & repo links
│   ├── workspace/             # Simplified Workspace interface
│   │   ├── WorkspaceTopBar.tsx # Top bar with active dataset, sheet selector, replace file
│   │   └── WorkspaceSidebar.tsx # Responsive 8-section left navigation drawer
│   └── views/                 # Modular analytical views
│       ├── OverviewView.tsx
│       ├── DataPreviewView.tsx
│       ├── DataQualityView.tsx
│       ├── StatisticsView.tsx
│       ├── VisualizationsView.tsx
│       ├── CorrelationsView.tsx
│       ├── OutlierAnalysisView.tsx
│       └── ReportCenterView.tsx
├── src/                       # Pure Python analytical core
│   ├── data_loader.py         # CSV loader with encoding fallback
│   ├── excel_loader.py        # Multi-sheet Excel workbook inspector
│   ├── format_registry.py     # Universal format dispatcher & registry
│   ├── json_loader.py         # JSON & NDJSON / JSONL reader with flattening
│   ├── parquet_loader.py      # Apache Parquet columnar reader
│   ├── tsv_loader.py          # Tab-separated value parser
│   ├── text_log_loader.py     # Text & structured log analyzer
│   ├── xml_loader.py          # Hardened, safe XML parser
│   ├── data_overview.py       # Dimensions & semantic classifications
│   ├── data_quality.py        # Health heuristics & missing value audits
│   ├── statistics.py          # Numeric & categorical statistics
│   ├── outliers.py            # Tukey IQR anomaly detection
│   ├── visualizations.py      # Plotly chart figure generators
│   └── report_generator.py    # Multi-tab XLSX & Complete ZIP generator
├── sample_data/               # Curated sample datasets
│   ├── sample_superstore_eda.csv
│   ├── sample_analytix_multisheet.xlsx
│   ├── sample_tech_inventory.json
│   ├── sample_student_scores.tsv
│   ├── sample_web_analytics.parquet
│   └── sample_server_access.log
├── tests/                     # 100 automated pytest tests
│   ├── test_api_endpoints.py
│   ├── test_data_loader.py
│   ├── test_excel_loader.py
│   ├── test_format_registry.py
│   ├── test_json_loader.py
│   ├── test_parquet_loader.py
│   ├── test_tsv_loader.py
│   ├── test_text_log_loader.py
│   ├── test_xml_loader.py
│   ├── test_report_generator.py
│   └── ...
├── next.config.mjs            # Next.js configuration & dev proxy rewrites
├── vercel.json                # Vercel serverless routing configuration
└── requirements.txt           # Python backend dependencies
```

---

## 🚀 Getting Started Locally

### Prerequisites
- **Node.js**: v18.17+ or v20+
- **Python**: 3.10+ (tested through 3.14)

### 1. Clone the Repository
```bash
git clone https://github.com/bhvyshrm/csv-explorer.git
cd csv-explorer
```

### 2. Set Up Python Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Test Suite
```bash
pytest
```
*All 100 tests should pass.*

### 4. Install Frontend Dependencies & Start Development Server
```bash
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

In development, Next.js automatically proxies API calls to the local FastAPI backend (or you can run `uvicorn api.index:app --reload --port 8000` concurrently).

### 5. Production Build Verification
```bash
npm run build
```

---

## 🌐 Deployment on Vercel

Analytix is architected specifically for frictionless zero-config deployment on [Vercel](https://vercel.com):

1. **Next.js Frontend**: Built and deployed automatically via `@vercel/next`.
2. **Serverless Python Backend**: Route `/api/*` requests directly to `api/index.py` via `vercel.json` and ASGI path restoration middleware in `api/index.py`.
3. **Payload Limits**: Max file upload size is bounded at 4.5 MB to strictly satisfy Vercel Serverless payload limits.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
