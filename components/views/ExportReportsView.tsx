"use client";

import React, { useState } from "react";
import { AnalysisPayload } from "@/types/analytix";
import { Download, FileJson, FileText, CheckCircle2 } from "lucide-react";

interface ExportReportsViewProps {
  data: AnalysisPayload;
}

export default function ExportReportsView({ data }: ExportReportsViewProps) {
  const [downloadSuccess, setDownloadSuccess] = useState<string | null>(null);

  const filePrefix = data.dataset_name
    .replace(".xlsx", "")
    .replace(".csv", "")
    .replace(".xls", "");
  const activePrefix = data.active_worksheet
    ? `${filePrefix}_${data.active_worksheet}`
    : filePrefix;

  const triggerDownload = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
    setDownloadSuccess(filename);
    setTimeout(() => setDownloadSuccess(null), 3000);
  };

  const handleExportMetadataCSV = () => {
    const headers = [
      "Column Name",
      "Inferred Type",
      "Python dtype",
      "Missing Count",
      "Missing %",
      "Unique Values",
      "Memory (Bytes)",
    ];
    const rows = data.columns.map((c) =>
      [
        `"${c["Column Name"]}"`,
        `"${c["Inferred Type"]}"`,
        `"${c["Python dtype"]}"`,
        c["Missing Count"],
        c["Missing %"],
        c["Unique Values"],
        c["Memory (Bytes)"],
      ].join(",")
    );
    triggerDownload(
      [headers.join(","), ...rows].join("\n"),
      `${activePrefix}_column_metadata.csv`,
      "text/csv;charset=utf-8;"
    );
  };

  const handleExportMissingValuesCSV = () => {
    const headers = ["Column", "Missing Count", "Missing %", "Non-Missing Count"];
    const rows = data.quality.missing_summary.detail_table.map((r) =>
      [`"${r.Column}"`, r["Missing Count"], r["Missing %"], r["Non-Missing Count"]].join(
        ","
      )
    );
    triggerDownload(
      [headers.join(","), ...rows].join("\n"),
      `${activePrefix}_missing_values.csv`,
      "text/csv;charset=utf-8;"
    );
  };

  const handleExportNumericStatsCSV = () => {
    if (data.numeric_statistics.length === 0) return;
    const cols = Object.keys(data.numeric_statistics[0]);
    const headers = cols.map((c) => `"${c}"`).join(",");
    const rows = data.numeric_statistics.map((r) =>
      cols
        .map((c) => {
          const val = r[c];
          if (val === null || val === undefined) return "";
          return `"${String(val).replace(/"/g, '""')}"`;
        })
        .join(",")
    );
    triggerDownload(
      [headers, ...rows].join("\n"),
      `${activePrefix}_numeric_statistics.csv`,
      "text/csv;charset=utf-8;"
    );
  };

  const handleExportDuplicatesCSV = () => {
    if (data.quality.duplicate_summary.preview.length === 0) return;
    const cols = Object.keys(data.quality.duplicate_summary.preview[0]);
    const headers = cols.map((c) => `"${c}"`).join(",");
    const rows = data.quality.duplicate_summary.preview.map((r) =>
      cols
        .map((c) => {
          const val = r[c];
          if (val === null || val === undefined) return "";
          return `"${String(val).replace(/"/g, '""')}"`;
        })
        .join(",")
    );
    triggerDownload(
      [headers, ...rows].join("\n"),
      `${activePrefix}_duplicate_rows.csv`,
      "text/csv;charset=utf-8;"
    );
  };

  const handleExportConsolidatedJSON = () => {
    const reportData = {
      application: "Analytix",
      version: "2.0.0",
      generated_at_utc: new Date().toISOString(),
      dataset_name: data.dataset_name,
      dataset_format: data.dataset_format,
      ...(data.active_worksheet ? { active_worksheet: data.active_worksheet } : {}),
      overview: {
        total_rows: data.overview.total_rows,
        total_columns: data.overview.total_columns,
        memory_usage_bytes: data.overview.memory_usage_bytes,
        total_duplicate_rows: data.overview.total_duplicate_rows,
        numeric_columns_count: data.overview.numeric_columns.length,
        categorical_columns_count: data.overview.categorical_columns.length,
      },
      columns: data.columns,
      quality: {
        status: data.quality.status,
        overall_health_score: data.quality.overall_health_score,
        total_missing_cells: data.quality.missing_summary.total_missing_cells,
        missing_cells_pct: data.quality.missing_summary.missing_cells_pct,
        total_duplicates: data.quality.duplicate_summary.total_duplicates,
        constant_columns: data.quality.variance_summary.constant_columns,
        entirely_empty_columns: data.quality.variance_summary.entirely_empty_columns,
        nearly_empty_columns: data.quality.variance_summary.nearly_empty_columns,
        issues: data.quality.issues,
      },
      numeric_statistics: data.numeric_statistics,
    };

    triggerDownload(
      JSON.stringify(reportData, null, 2),
      `${activePrefix}_eda_report.json`,
      "application/json;charset=utf-8;"
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-card border border-border rounded-xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-primary-text flex items-center gap-2">
              <Download className="w-5 h-5 text-accent" />
              Export & Analytical Reports
            </h1>
            <p className="text-sm text-muted-text mt-0.5">
              Generate standardized tabular CSV summaries or a consolidated, JSON-safe programmatic EDA report.
            </p>
          </div>

          {downloadSuccess && (
            <div className="flex items-center gap-2 bg-success/10 border border-success/30 text-success text-xs px-3 py-1.5 rounded-lg animate-fade-in font-mono">
              <CheckCircle2 className="w-4 h-4" />
              <span>Downloaded: {downloadSuccess}</span>
            </div>
          )}
        </div>
      </div>

      {/* Export Options Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* CSV Modular Exports Card */}
        <div className="bg-card border border-border rounded-xl p-6 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="p-2 rounded-lg bg-accent/10 border border-accent/30 text-accent">
                <FileText className="w-4 h-4" />
              </div>
              <h3 className="font-semibold text-primary-text text-base">
                Tabular CSV Exports
              </h3>
            </div>
            <p className="text-xs text-muted-text leading-relaxed">
              Download clean, standardized tabular summaries formatted for spreadsheet software or downstream modeling pipelines.
            </p>
          </div>

          <div className="space-y-2.5 pt-2">
            <button
              onClick={handleExportMetadataCSV}
              className="w-full flex items-center justify-between bg-background border border-border hover:border-accent text-primary-text px-4 py-2.5 rounded-lg text-xs font-mono transition-colors"
            >
              <span>Column Metadata & Overview (CSV)</span>
              <Download className="w-3.5 h-3.5 text-accent" />
            </button>

            <button
              onClick={handleExportMissingValuesCSV}
              className="w-full flex items-center justify-between bg-background border border-border hover:border-accent text-primary-text px-4 py-2.5 rounded-lg text-xs font-mono transition-colors"
            >
              <span>Missing Values Audit (CSV)</span>
              <Download className="w-3.5 h-3.5 text-accent" />
            </button>

            {data.numeric_statistics.length > 0 && (
              <button
                onClick={handleExportNumericStatsCSV}
                className="w-full flex items-center justify-between bg-background border border-border hover:border-accent text-primary-text px-4 py-2.5 rounded-lg text-xs font-mono transition-colors"
              >
                <span>Numeric Descriptive Statistics (CSV)</span>
                <Download className="w-3.5 h-3.5 text-accent" />
              </button>
            )}

            {data.quality.duplicate_summary.total_duplicates > 0 && (
              <button
                onClick={handleExportDuplicatesCSV}
                className="w-full flex items-center justify-between bg-background border border-border hover:border-accent text-primary-text px-4 py-2.5 rounded-lg text-xs font-mono transition-colors"
              >
                <span>Flagged Duplicate Rows (CSV)</span>
                <Download className="w-3.5 h-3.5 text-accent" />
              </button>
            )}
          </div>
        </div>

        {/* Consolidated JSON Report Card */}
        <div className="bg-card border border-border rounded-xl p-6 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="p-2 rounded-lg bg-teal-950/40 border border-teal-800/40 text-accent-secondary">
                <FileJson className="w-4 h-4" />
              </div>
              <h3 className="font-semibold text-primary-text text-base">
                Consolidated JSON EDA Report
              </h3>
            </div>
            <p className="text-xs text-muted-text leading-relaxed">
              Programmatic, machine-readable JSON report including dataset format, active sheet metadata, dimensions, quality heuristics, and numeric distributions.
            </p>
          </div>

          <div className="bg-background/80 border border-border/80 rounded-lg p-3 text-[11px] font-mono text-muted-text space-y-1">
            <div>Target: {data.dataset_name}</div>
            <div>Format: {data.dataset_format}</div>
            {data.active_worksheet && <div>Worksheet: {data.active_worksheet}</div>}
            <div>Health Score: {data.quality.overall_health_score.toFixed(0)}/100</div>
          </div>

          <button
            onClick={handleExportConsolidatedJSON}
            className="w-full flex items-center justify-center gap-2 bg-accent hover:bg-accent/90 text-white font-medium py-3 rounded-lg text-xs font-mono transition-all shadow-md"
          >
            <Download className="w-4 h-4" />
            <span>Download Consolidated JSON Report</span>
          </button>
        </div>
      </div>
    </div>
  );
}
