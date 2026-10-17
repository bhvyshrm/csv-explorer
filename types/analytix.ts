export interface DatasetOverview {
  total_rows: number;
  total_columns: number;
  total_cells: number;
  memory_usage_bytes: number;
  memory_usage_formatted: string;
  total_duplicate_rows: number;
  duplicate_rows_pct: number;
  total_missing_cells: number;
  missing_cells_pct: number;
  numeric_columns: string[];
  categorical_columns: string[];
  datetime_columns: string[];
  boolean_columns: string[];
}

export interface ColumnMetadata {
  "Column Name": string;
  "Inferred Type": string;
  "Python dtype": string;
  "Missing Count": number;
  "Missing %": number;
  "Unique Values": number;
  "Memory (Bytes)": number;
}

export interface QualityIssue {
  title: string;
  description: string;
  severity: "INFO" | "WARNING" | "CRITICAL";
  affected_columns: string[];
}

export interface MissingValueRow {
  Column: string;
  "Missing Count": number;
  "Missing %": number;
  "Non-Missing Count": number;
}

export interface MissingSummary {
  total_missing_cells: number;
  missing_cells_pct: number;
  columns_with_missing_count: number;
  detail_table: MissingValueRow[];
}

export interface DuplicateSummary {
  total_duplicates: number;
  duplicate_pct: number;
  rows_remaining_after_dedup: number;
  preview: Record<string, any>[];
}

export interface VarianceSummary {
  constant_columns: Record<string, any>;
  entirely_empty_columns: string[];
  nearly_empty_columns: string[];
  threshold_pct: number;
}

export interface QualityReport {
  status: string;
  overall_health_score: number;
  issues: QualityIssue[];
  missing_summary: MissingSummary;
  duplicate_summary: DuplicateSummary;
  variance_summary: VarianceSummary;
}

export interface CategoricalFrequencyRow {
  Category: string;
  Count: number;
  Percentage: number;
}

export interface CategoricalStatistic {
  unique_count: number;
  most_frequent_value: string;
  frequency_table: CategoricalFrequencyRow[];
}

export interface SheetMetadata {
  name: string;
  row_count: number;
  col_count: number;
  sample_headers: string[];
  is_empty: boolean;
}

export interface WorkbookMetadata {
  file_format: string;
  total_sheets: number;
  sheet_names: string[];
  sheets: SheetMetadata[];
}

export interface OutlierResult {
  column: string;
  valid_observations_count: number;
  q1: number | null;
  q3: number | null;
  iqr: number | null;
  multiplier: number;
  lower_bound: number | null;
  upper_bound: number | null;
  flagged_count: number;
  lower_outliers_count: number;
  upper_outliers_count: number;
  flagged_pct: number;
  status_message: string;
  flagged_preview: Record<string, any>[];
}

export interface PlotlyFigureSpec {
  data: any[];
  layout: Record<string, any>;
}

export interface VisualizationsMap {
  missing_values?: PlotlyFigureSpec | null;
  histograms: Record<string, PlotlyFigureSpec | null>;
  box_plots: Record<string, PlotlyFigureSpec | null>;
  category_bars: Record<string, PlotlyFigureSpec | null>;
  correlation_heatmap?: PlotlyFigureSpec | null;
}

export interface AnalysisPayload {
  dataset_name: string;
  dataset_format: string;
  active_worksheet: string | null;
  workbook_metadata: WorkbookMetadata | null;
  overview: DatasetOverview;
  columns: ColumnMetadata[];
  preview: Record<string, any>[];
  quality: QualityReport;
  numeric_statistics: Record<string, any>[];
  categorical_statistics: Record<string, CategoricalStatistic>;
  visualizations: VisualizationsMap;
  outliers: Record<string, OutlierResult | null>;
}

export type ActiveNavTab =
  | "overview"
  | "data-preview"
  | "data-quality"
  | "statistics"
  | "visualizations"
  | "correlations"
  | "outliers"
  | "reports"
  // Legacy aliases for backward compatibility
  | "data-explorer"
  | "excel-explorer"
  | "outlier-analysis"
  | "export-reports";

export interface SampleDatasetItem {
  id: string;
  name: string;
  format: string;
  description: string;
  endpoint: string;
  rows: number;
  cols: number;
  badge: string;
}

export interface FormatDescriptorItem {
  id: string;
  name: string;
  description: string;
  extensions: string[];
  is_available: boolean;
  status_label: string;
  category: string;
}
