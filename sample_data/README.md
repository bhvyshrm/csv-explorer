# Analytix Sample Datasets

This directory contains deterministic sample datasets designed to validate data ingestion, exploratory data profiling, data quality auditing, and outlier detection across multiple file formats.

---

## 1. Multi-Sheet Excel Workbook: `sample_analytix_multisheet.xlsx`

A modern `.xlsx` workbook containing three distinct worksheets to demonstrate Analytix's **Excel Explorer** capabilities:

### Sheet 1: `Orders_Data` (101 Rows, 8 Columns)
- **`Order_ID`**: Alphanumeric order tracking code.
- **`Order_Date`**: Datetime object verifying automatic Excel date parsing.
- **`Region`**: Geographic segment (contains ~5% missing values).
- **`Category`**: High-level retail category.
- **`Sales`**: Order revenue in USD (contains extreme positive outliers up to \$4,950).
- **`Quantity`**: Discrete purchase count (1-10 units).
- **`Profit`**: Financial margin (contains missing values and negative margin outliers down to -\$850).
- **`Is_Returned`**: Boolean status flag (`True`/`False`).
- **Includes 1 duplicate row** to verify duplicate detection on Excel datasets.

### Sheet 2: `Customer_Demographics` (50 Rows, 7 Columns)
- **`Customer_ID`**: Identifier code.
- **`Customer_Name`**: Anonymized customer label.
- **`Age`**: Customer age (contains null entries).
- **`Segment`**: Market segmentation (`Consumer`, `Corporate`, `Small Business`).
- **`Country`**: Constant value (`"United States"`) to verify zero-variance column detection on Excel sheets.
- **`Income`**: Annual household income.
- **`Loyalty_Years`**: Continuous tenure duration.

### Sheet 3: `Empty_Template` (0 Rows, 3 Columns)
- An empty template containing headers (`Template_Field_A`, `Template_Field_B`, `Template_Field_C`) and 0 data rows to test edge-case handling for blank/header-only worksheets.

---

## 2. CSV Dataset: `sample_superstore_eda.csv`

A 122-row, 16-column retail transaction dataset formatted as standard CSV:
- **Missing Values**: Columns `Region`, `Customer_Age`, `Discount`, and `Shipping_Cost` include intentional missing cells.
- **Duplicate Rows**: Includes 2 exact duplicated records.
- **Constant Column**: `Store_Status` contains 1 unique value across all rows (`"Active"`).
- **Outliers**: Extreme values in `Sales` (\$5,200) and `Profit` (-\$1,250).
