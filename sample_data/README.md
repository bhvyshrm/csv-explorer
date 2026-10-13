# Sample Dataset: Superstore EDA Transactions

This dataset (`sample_superstore_eda.csv`) provides a realistic, multi-attribute e-commerce retail sales dataset tailored for exploratory data analysis, quality assessment, and outlier evaluation.

## Dataset Structure

- **Rows**: 122 observations
- **Columns**: 16 fields

## Column Descriptions

| Column | Type | Description | Analytical Purpose |
| :--- | :--- | :--- | :--- |
| `Order_ID` | String | Unique order reference code | Primary identifier |
| `Order_Date` | Date String | ISO 8601 transaction date (`YYYY-MM-DD`) | Temporal dimension |
| `Region` | String | Geographical territory (West, East, Central, South) | Contains ~5% missing values |
| `Customer_Segment` | String | Market segment (Consumer, Corporate, Home Office) | Categorical breakdown |
| `Customer_Age` | Numeric | Customer age in years | Contains ~5% missing values |
| `Category` | String | High-level product category | Categorical distribution |
| `Sub_Category` | String | Specific product subcategory | Multi-level category analysis |
| `Order_Priority` | String | Fulfillment priority (Critical, High, Medium, Low) | Ordinal frequency analysis |
| `Payment_Method` | String | Transaction payment provider | Categorical distribution |
| `Sales` | Numeric | Order total in USD | Contains intentional positive outliers |
| `Quantity` | Integer | Units purchased (1-12) | Discrete count distribution |
| `Discount` | Float | Promotional markdown rate (0.0 to 0.3) | Continuous rate with missing entries |
| `Profit` | Numeric | Net profit in USD | Contains intentional negative outliers |
| `Shipping_Cost` | Numeric | Logistics freight charge | Contains ~3% missing values |
| `Is_Returned` | Boolean | Whether product was returned (`True`/`False`) | Binary flag |
| `Store_Status` | String | Constant value (`"Active"`) | Validates constant column detection |

## Built-in Data Quality Test Cases

1. **Missing Values**: Columns `Region`, `Customer_Age`, `Discount`, and `Shipping_Cost` include missing values to test null indicators and missing value charts.
2. **Duplicate Rows**: Includes 2 exact duplicated records to test duplicate row detection.
3. **Constant Column**: `Store_Status` contains 1 unique value across all rows to verify low-variance / constant column detection.
4. **Outliers**: `Sales` contains extreme positive values (e.g., \$4,850 and \$5,200), and `Profit` contains significant negative margins (e.g., -\$1,250) to verify IQR outlier detection.
