"use client";

import React, { useState } from "react";
import { AnalysisPayload } from "@/types/analytix";
import {
  Download,
  FileSpreadsheet,
  FileCode,
  FileText,
  CheckCircle2,
  Package,
  Layers,
  Loader2,
  FileCheck,
  ShieldCheck,
  AlertCircle,
} from "lucide-react";

interface ReportCenterViewProps {
  data: AnalysisPayload;
}

export default function ReportCenterView({ data }: ReportCenterViewProps) {
  const [downloadingType, setDownloadingType] = useState<string | null>(null);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const cleanPrefix = data.dataset_name
    .replace(".xlsx", "")
    .replace(".csv", "")
    .replace(".xls", "")
    .replace(".json", "")
    .replace(".parquet", "")
    .replace(".tsv", "")
    .replace(".txt", "")
    .replace(".log", "")
    .replace(".xml", "");

  const activePrefix = data.active_worksheet
    ? `${cleanPrefix}_${data.active_worksheet}`
    : cleanPrefix;

  const triggerBlobDownload = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setSuccessNotice(`Successfully downloaded: ${filename}`);
    setTimeout(() => setSuccessNotice(null), 4000);
  };

  // 1. Download Complete ZIP
  const handleDownloadCompleteZIP = async () => {
    setDownloadingType("zip");
    setErrorMessage(null);
    try {
      const res = await fetch("/api/export/zip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          filename: data.dataset_name,
          dataset_format: data.dataset_format,
          active_worksheet: data.active_worksheet,
          overview: data.overview,
          columns: data.columns,
          quality: data.quality,
          numeric_stats: data.numeric_statistics,
          outliers: data.outliers,
          preview: data.preview,
        }),
      });

      if (!res.ok) throw new Error("Failed to generate ZIP archive.");
      const blob = await res.blob();
      triggerBlobDownload(blob, `${activePrefix}_complete_analysis_archive.zip`);
    } catch (err: any) {
      setErrorMessage(err.message || "Error generating complete report archive.");
    } finally {
      setDownloadingType(null);
    }
  };

  // 2. Download Multi-Sheet Excel XLSX
  const handleDownloadXLSX = async () => {
    setDownloadingType("xlsx");
    setErrorMessage(null);
    try {
      const res = await fetch("/api/export/xlsx", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          filename: data.dataset_name,
          dataset_format: data.dataset_format,
          active_worksheet: data.active_worksheet,
          overview: data.overview,
          columns: data.columns,
          quality: data.quality,
          numeric_stats: data.numeric_statistics,
          outliers: data.outliers,
        }),
      });

      if (!res.ok) throw new Error("Failed to generate Excel workbook.");
      const blob = await res.blob();
      triggerBlobDownload(blob, `${activePrefix}_analysis_workbook.xlsx`);
    } catch (err: any) {
      setErrorMessage(err.message || "Error generating Excel workbook.");
    } finally {
      setDownloadingType(null);
    }
  };

  // 3. Download HTML Executive Summary
  const handleDownloadHTML = async () => {
    setDownloadingType("html");
    setErrorMessage(null);
    try {
      const res = await fetch("/api/export/html", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          filename: data.dataset_name,
          dataset_format: data.dataset_format,
          active_worksheet: data.active_worksheet,
          overview: data.overview,
          columns: data.columns,
          quality: data.quality,
        }),
      });

      if (!res.ok) throw new Error("Failed to generate HTML summary report.");
      const blob = await res.blob();
      triggerBlobDownload(blob, `${activePrefix}_executive_summary.html`);
    } catch (err: any) {
      setErrorMessage(err.message || "Error generating HTML report.");
    } finally {
      setDownloadingType(null);
    }
  };

  // 4. Download Consolidated JSON Report
  const handleDownloadJSON = () => {
    const jsonReport = {
      application: "Analytix",
      generated_at_utc: new Date().toISOString(),
      dataset_name: data.dataset_name,
      dataset_format: data.dataset_format,
      active_worksheet: data.active_worksheet,
      overview: data.overview,
      columns: data.columns,
      quality: data.quality,
      numeric_statistics: data.numeric_statistics,
      outliers: data.outliers,
    };
    const blob = new Blob([JSON.stringify(jsonReport, null, 2)], {
      type: "application/json;charset=utf-8;",
    });
    triggerBlobDownload(blob, `${activePrefix}_eda_report.json`);
  };

  // CSV Modular triggers
  const handleDownloadCSV = (content: string, suffix: string) => {
    const blob = new Blob([content], { type: "text/csv;charset=utf-8;" });
    triggerBlobDownload(blob, `${activePrefix}_${suffix}.csv`);
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
    handleDownloadCSV([headers.join(","), ...rows].join("\n"), "column_metadata");
  };

  const handleExportMissingValuesCSV = () => {
    const headers = ["Column", "Missing Count", "Missing %", "Non-Missing Count"];
    const rows = data.quality.missing_summary.detail_table.map((r) =>
      [`"${r.Column}"`, r["Missing Count"], r["Missing %"], r["Non-Missing Count"]].join(",")
    );
    handleDownloadCSV([headers.join(","), ...rows].join("\n"), "missing_values");
  };

  const handleExportStatsCSV = () => {
    if (data.numeric_statistics.length === 0) return;
    const cols = Object.keys(data.numeric_statistics[0]);
    const headers = cols.map((c) => `"${c}"`).join(",");
    const rows = data.numeric_statistics.map((r) =>
      cols.map((c) => `"${String(r[c] ?? "").replace(/"/g, '""')}"`).join(",")
    );
    handleDownloadCSV([headers, ...rows].join("\n"), "numeric_statistics");
  };

  const handleExportDuplicatesCSV = () => {
    if (data.quality.duplicate_summary.preview.length === 0) return;
    const cols = Object.keys(data.quality.duplicate_summary.preview[0]);
    const headers = cols.map((c) => `"${c}"`).join(",");
    const rows = data.quality.duplicate_summary.preview.map((r) =>
      cols.map((c) => `"${String(r[c] ?? "").replace(/"/g, '""')}"`).join(",")
    );
    handleDownloadCSV([headers, ...rows].join("\n"), "duplicate_rows");
  };

  const handleExportOutliersCSV = () => {
    const outlierRows: any[] = [];
    Object.entries(data.outliers).forEach(([col, o]) => {
      if (o) {
        outlierRows.push({
          Column: col,
          Q1: o.q1,
          Q3: o.q3,
          IQR: o.iqr,
          Lower_Bound: o.lower_bound,
          Upper_Bound: o.upper_bound,
          Flagged_Count: o.flagged_count,
          Flagged_Pct: `${o.flagged_pct.toFixed(2)}%`,
        });
      }
    });
    if (outlierRows.length === 0) return;
    const cols = Object.keys(outlierRows[0]);
    const headers = cols.join(",");
    const rows = outlierRows.map((r) => cols.map((c) => `"${r[c] ?? ""}"`).join(","));
    handleDownloadCSV([headers, ...rows].join("\n"), "outliers_report");
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-3xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <Download className="w-5 h-5 text-indigo-600" />
              Professional Report Center
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Download comprehensive analysis archives, multi-tab Excel workbooks, or modular CSV tables for {data.dataset_name}.
            </p>
          </div>

          {successNotice && (
            <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs px-3.5 py-2 rounded-2xl animate-fade-in font-mono">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>{successNotice}</span>
            </div>
          )}

          {errorMessage && (
            <div className="flex items-center gap-2 bg-rose-50 border border-rose-200 text-rose-800 text-xs px-3.5 py-2 rounded-2xl animate-fade-in font-mono">
              <AlertCircle className="w-4 h-4 text-rose-600" />
              <span>{errorMessage}</span>
            </div>
          )}
        </div>
      </div>

      {/* Featured Primary Export Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Card 1: Complete ZIP Archive */}
        <div className="bg-gradient-to-br from-indigo-50/80 to-purple-50/60 border border-indigo-200/80 rounded-3xl p-6 shadow-sm flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="p-2 rounded-2xl bg-indigo-600 text-white shadow-xs">
                <Package className="w-5 h-5" />
              </div>
              <span className="text-[10px] font-mono uppercase tracking-wider font-bold bg-indigo-100 text-indigo-800 px-2.5 py-0.5 rounded-full">
                All-in-One
              </span>
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-1">
              Complete Analysis Archive
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Consolidated ZIP archive containing executive HTML summary, multi-sheet XLSX workbook, JSON report, and all modular CSV tables.
            </p>
          </div>

          <button
            onClick={handleDownloadCompleteZIP}
            disabled={downloadingType !== null}
            className="w-full flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 text-white py-3 rounded-2xl text-xs font-semibold shadow-sm transition-all disabled:opacity-50"
          >
            {downloadingType === "zip" ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            <span>Download All Reports (.ZIP)</span>
          </button>
        </div>

        {/* Card 2: Multi-tab Excel XLSX */}
        <div className="bg-gradient-to-br from-emerald-50/80 to-teal-50/60 border border-emerald-200/80 rounded-3xl p-6 shadow-sm flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="p-2 rounded-2xl bg-emerald-600 text-white shadow-xs">
                <FileSpreadsheet className="w-5 h-5" />
              </div>
              <span className="text-[10px] font-mono uppercase tracking-wider font-bold bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded-full">
                Multi-Tab
              </span>
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-1">
              Excel Analysis Workbook
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Styled multi-sheet .xlsx workbook containing Overview, Columns, Quality, Statistics, Correlations, and Outliers.
            </p>
          </div>

          <button
            onClick={handleDownloadXLSX}
            disabled={downloadingType !== null}
            className="w-full flex items-center justify-center gap-2 bg-emerald-700 hover:bg-emerald-800 text-white py-3 rounded-2xl text-xs font-semibold shadow-sm transition-all disabled:opacity-50"
          >
            {downloadingType === "xlsx" ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            <span>Download Workbook (.XLSX)</span>
          </button>
        </div>

        {/* Card 3: Executive Summary HTML */}
        <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-3xl p-6 shadow-sm flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="p-2 rounded-2xl bg-slate-900 text-white shadow-xs">
                <FileCheck className="w-5 h-5" />
              </div>
              <span className="text-[10px] font-mono uppercase tracking-wider font-bold bg-slate-100 text-slate-700 px-2.5 py-0.5 rounded-full">
                Print / PDF Ready
              </span>
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-1">
              Executive Summary Report
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Clean, standalone HTML document formatted for executive review, sharing, or direct saving to PDF.
            </p>
          </div>

          <button
            onClick={handleDownloadHTML}
            disabled={downloadingType !== null}
            className="w-full flex items-center justify-center gap-2 bg-white hover:bg-slate-50 border border-slate-300 text-slate-800 py-3 rounded-2xl text-xs font-semibold shadow-xs transition-all disabled:opacity-50"
          >
            {downloadingType === "html" ? (
              <Loader2 className="w-4 h-4 animate-spin text-slate-700" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            <span>Download Summary (.HTML)</span>
          </button>
        </div>
      </div>

      {/* Individual Modular Exports Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* CSV Modular Tables */}
        <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-3xl p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-slate-100 text-slate-800">
              <FileText className="w-4 h-4 text-indigo-600" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">Modular Tabular CSVs</h3>
              <p className="text-[11px] text-slate-500">Download specific analytical tables</p>
            </div>
          </div>

          <div className="space-y-2 pt-1">
            <button
              onClick={handleExportMetadataCSV}
              className="w-full flex items-center justify-between bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-800 px-4 py-2.5 rounded-xl text-xs font-mono transition-colors"
            >
              <span>Column Metadata & Types (CSV)</span>
              <Download className="w-3.5 h-3.5 text-slate-500" />
            </button>

            <button
              onClick={handleExportMissingValuesCSV}
              className="w-full flex items-center justify-between bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-800 px-4 py-2.5 rounded-xl text-xs font-mono transition-colors"
            >
              <span>Missing Values Audit (CSV)</span>
              <Download className="w-3.5 h-3.5 text-slate-500" />
            </button>

            {data.numeric_statistics.length > 0 && (
              <button
                onClick={handleExportStatsCSV}
                className="w-full flex items-center justify-between bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-800 px-4 py-2.5 rounded-xl text-xs font-mono transition-colors"
              >
                <span>Descriptive Statistics (CSV)</span>
                <Download className="w-3.5 h-3.5 text-slate-500" />
              </button>
            )}

            {data.quality.duplicate_summary.total_duplicates > 0 && (
              <button
                onClick={handleExportDuplicatesCSV}
                className="w-full flex items-center justify-between bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-800 px-4 py-2.5 rounded-xl text-xs font-mono transition-colors"
              >
                <span>Flagged Duplicate Rows (CSV)</span>
                <Download className="w-3.5 h-3.5 text-slate-500" />
              </button>
            )}

            <button
              onClick={handleExportOutliersCSV}
              className="w-full flex items-center justify-between bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-800 px-4 py-2.5 rounded-xl text-xs font-mono transition-colors"
            >
              <span>Outliers Summary Report (CSV)</span>
              <Download className="w-3.5 h-3.5 text-slate-500" />
            </button>
          </div>
        </div>

        {/* Machine-Readable JSON Export */}
        <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-3xl p-6 shadow-sm space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2.5 mb-3">
              <div className="p-2 rounded-xl bg-purple-100 text-purple-700">
                <FileCode className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">Programmatic JSON Report</h3>
                <p className="text-[11px] text-slate-500">Machine-readable audit format</p>
              </div>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Consolidated JSON document containing complete dataset dimensions, inferred types, quality audit results, and statistical metrics.
            </p>
          </div>

          <div className="bg-slate-50 border border-slate-200/70 rounded-2xl p-3 text-[11px] font-mono text-slate-600 space-y-1">
            <div>Target: {data.dataset_name}</div>
            <div>Format: {data.dataset_format}</div>
            <div>Quality Score: {data.quality.overall_health_score.toFixed(1)}/100</div>
          </div>

          <button
            onClick={handleDownloadJSON}
            className="w-full flex items-center justify-center gap-2 bg-purple-700 hover:bg-purple-800 text-white py-3 rounded-2xl text-xs font-semibold shadow-xs transition-all"
          >
            <Download className="w-4 h-4" />
            <span>Download Structured JSON</span>
          </button>
        </div>
      </div>
    </div>
  );
}
