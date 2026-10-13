"""Analytix - Multi-Format Data Exploration Platform.

Core modules:
- data_loader: CSV ingestion, encoding fallback, validation.
- excel_loader: Excel workbook (.xlsx, .xls) multi-sheet discovery, parsing, and inspection.
- data_overview: Dataset dimensions, column types, memory.
- data_quality: Missing values, duplicates, constant/empty columns.
- statistics: Numeric descriptive statistics and categorical frequencies.
- visualizations: Interactive Plotly visualizations and heatmaps.
- outliers: Interquartile Range (IQR) outlier detection.
- export: Clean CSV and JSON reporting with worksheet metadata support.
"""

__version__ = "2.0.0"
