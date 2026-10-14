"use client";

import React, { useState } from "react";
import { AnalysisPayload, QualityIssue } from "@/types/analytix";
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Info,
  Copy,
  Sliders,
  HelpCircle,
} from "lucide-react";

interface DataQualityViewProps {
  data: AnalysisPayload;
}

export default function DataQualityView({ data }: DataQualityViewProps) {
  const { quality } = data;
  const [activeTab, setActiveTab] = useState<"issues" | "missing" | "duplicates" | "variance">("issues");

  const score = quality.overall_health_score;
  const isHealthy = score >= 85;
  const isModerate = score >= 65 && score < 85;

  const scoreColor = isHealthy
    ? "text-success border-success/30 bg-success/10"
    : isModerate
    ? "text-warning border-warning/30 bg-warning/10"
    : "text-danger border-danger/30 bg-danger/10";

  const getSeverityBadge = (severity: string) => {
    switch (severity.toUpperCase()) {
      case "CRITICAL":
        return {
          icon: ShieldAlert,
          classes: "bg-red-950/40 text-red-300 border-red-800/40",
        };
      case "WARNING":
        return {
          icon: AlertTriangle,
          classes: "bg-amber-950/40 text-amber-300 border-amber-800/40",
        };
      default:
        return {
          icon: Info,
          classes: "bg-blue-950/40 text-blue-300 border-blue-800/40",
        };
    }
  };

  return (
    <div className="space-y-6">
      {/* Health Score Overview Card */}
      <div className="bg-card border border-border rounded-xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center gap-5">
            <div
              className={`w-20 h-20 rounded-2xl flex flex-col items-center justify-center border font-mono ${scoreColor}`}
            >
              <span className="text-2xl font-extrabold tracking-tight">
                {score.toFixed(0)}
              </span>
              <span className="text-[10px] uppercase tracking-wider font-semibold">
                Score
              </span>
            </div>

            <div>
              <div className="flex items-center gap-2">
                {isHealthy ? (
                  <ShieldCheck className="w-5 h-5 text-success" />
                ) : (
                  <ShieldAlert className="w-5 h-5 text-warning" />
                )}
                <h1 className="text-xl font-bold text-primary-text">
                  Data Quality Diagnostic Health
                </h1>
              </div>
              <p className="text-sm font-medium text-muted-text mt-1">
                Status: <span className="text-primary-text font-semibold">{quality.status}</span>
              </p>
              <p className="text-xs text-muted-text mt-0.5">
                Deterministic 0–100 heuristic calculated against missing values, duplicate rows, and zero-variance fields.
              </p>
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-3 gap-3 text-xs font-mono">
            <div className="bg-background/80 border border-border p-3 rounded-lg text-center">
              <span className="text-muted-text block text-[10px] uppercase">
                Missing Cells
              </span>
              <span className="text-sm font-bold text-primary-text">
                {quality.missing_summary.missing_cells_pct.toFixed(1)}%
              </span>
              <span className="text-[10px] text-muted-text block">
                {quality.missing_summary.total_missing_cells} cells
              </span>
            </div>

            <div className="bg-background/80 border border-border p-3 rounded-lg text-center">
              <span className="text-muted-text block text-[10px] uppercase">
                Duplicate Rows
              </span>
              <span className="text-sm font-bold text-primary-text">
                {quality.duplicate_summary.duplicate_pct.toFixed(1)}%
              </span>
              <span className="text-[10px] text-muted-text block">
                {quality.duplicate_summary.total_duplicates} rows
              </span>
            </div>

            <div className="bg-background/80 border border-border p-3 rounded-lg text-center">
              <span className="text-muted-text block text-[10px] uppercase">
                Constant Cols
              </span>
              <span className="text-sm font-bold text-primary-text">
                {Object.keys(quality.variance_summary.constant_columns).length}
              </span>
              <span className="text-[10px] text-muted-text block">
                0-variance
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-border text-sm font-medium">
        <button
          onClick={() => setActiveTab("issues")}
          className={`pb-3 px-4 border-b-2 font-medium transition-colors ${
            activeTab === "issues"
              ? "border-accent text-accent"
              : "border-transparent text-muted-text hover:text-primary-text"
          }`}
        >
          Diagnostic Issues ({quality.issues.length})
        </button>
        <button
          onClick={() => setActiveTab("missing")}
          className={`pb-3 px-4 border-b-2 font-medium transition-colors ${
            activeTab === "missing"
              ? "border-accent text-accent"
              : "border-transparent text-muted-text hover:text-primary-text"
          }`}
        >
          Missing Values Breakdown ({quality.missing_summary.columns_with_missing_count} cols)
        </button>
        <button
          onClick={() => setActiveTab("duplicates")}
          className={`pb-3 px-4 border-b-2 font-medium transition-colors ${
            activeTab === "duplicates"
              ? "border-accent text-accent"
              : "border-transparent text-muted-text hover:text-primary-text"
          }`}
        >
          Duplicate Rows ({quality.duplicate_summary.total_duplicates})
        </button>
        <button
          onClick={() => setActiveTab("variance")}
          className={`pb-3 px-4 border-b-2 font-medium transition-colors ${
            activeTab === "variance"
              ? "border-accent text-accent"
              : "border-transparent text-muted-text hover:text-primary-text"
          }`}
        >
          Variance & Sparsity
        </button>
      </div>

      {/* Tab 1: Issues List */}
      {activeTab === "issues" && (
        <div className="space-y-3">
          {quality.issues.length > 0 ? (
            quality.issues.map((issue: QualityIssue, idx: number) => {
              const badge = getSeverityBadge(issue.severity);
              const Icon = badge.icon;
              return (
                <div
                  key={idx}
                  className="bg-card border border-border rounded-xl p-4 flex items-start gap-4 hover:border-border/80 transition-colors"
                >
                  <div className={`p-2 rounded-lg border ${badge.classes} mt-0.5`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className={`text-[10px] uppercase tracking-wider font-mono px-2 py-0.5 rounded border font-semibold ${badge.classes}`}
                      >
                        {issue.severity}
                      </span>
                      <h3 className="font-semibold text-primary-text text-sm">
                        {issue.title}
                      </h3>
                    </div>
                    <p className="text-xs text-muted-text leading-relaxed">
                      {issue.description}
                    </p>
                    {issue.affected_columns && issue.affected_columns.length > 0 && (
                      <div className="flex flex-wrap items-center gap-1.5 mt-2">
                        <span className="text-[11px] text-muted-text/80 font-mono">
                          Affected fields:
                        </span>
                        {issue.affected_columns.map((col, cIdx) => (
                          <span
                            key={cIdx}
                            className="text-[11px] bg-background border border-border/80 text-primary-text px-2 py-0.5 rounded font-mono"
                          >
                            {col}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          ) : (
            <div className="bg-card border border-border rounded-xl p-8 text-center text-muted-text">
              <ShieldCheck className="w-10 h-10 text-success mx-auto mb-2" />
              <p className="text-sm font-medium text-primary-text">
                Zero data quality issues flagged!
              </p>
              <p className="text-xs text-muted-text mt-0.5">
                The dataset is clean and meets all diagnostic variance and completeness criteria.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Missing Values Table */}
      {activeTab === "missing" && (
        <div className="bg-card border border-border rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-background/80 border-b border-border uppercase text-muted-text">
                <tr>
                  <th className="py-3 px-4">Column</th>
                  <th className="py-3 px-4 text-right">Missing Count</th>
                  <th className="py-3 px-4 text-right">Missing %</th>
                  <th className="py-3 px-4 text-right">Non-Missing Count</th>
                  <th className="py-3 px-4 w-44">Completeness Ratio</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {quality.missing_summary.detail_table.map((row, idx) => {
                  const completenessPct = 100 - row["Missing %"];
                  return (
                    <tr key={idx} className="hover:bg-card-hover/60">
                      <td className="py-3 px-4 font-semibold text-primary-text">
                        {row.Column}
                      </td>
                      <td className="py-3 px-4 text-right text-primary-text">
                        {row["Missing Count"].toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <span
                          className={
                            row["Missing %"] > 0
                              ? "text-warning font-bold"
                              : "text-muted-text"
                          }
                        >
                          {row["Missing %"].toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right text-muted-text">
                        {row["Non-Missing Count"].toLocaleString()}
                      </td>
                      <td className="py-3 px-4">
                        <div className="w-full bg-background rounded-full h-2 overflow-hidden border border-border/80">
                          <div
                            className={`h-full rounded-full ${
                              completenessPct >= 95
                                ? "bg-success"
                                : completenessPct >= 70
                                ? "bg-warning"
                                : "bg-danger"
                            }`}
                            style={{ width: `${completenessPct}%` }}
                          />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Duplicates */}
      {activeTab === "duplicates" && (
        <div className="space-y-4">
          <div className="bg-card border border-border rounded-xl p-4 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-primary-text">
                Duplicate Rows Audit
              </h3>
              <p className="text-xs text-muted-text mt-0.5">
                Found {quality.duplicate_summary.total_duplicates} duplicate records (
                {quality.duplicate_summary.duplicate_pct.toFixed(2)}% of dataset).
                Rows remaining if deduplicated: {quality.duplicate_summary.rows_remaining_after_dedup.toLocaleString()}.
              </p>
            </div>
          </div>

          {quality.duplicate_summary.preview.length > 0 ? (
            <div className="bg-card border border-border rounded-xl overflow-hidden">
              <div className="overflow-x-auto max-h-96">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-background/90 sticky top-0 border-b border-border uppercase text-muted-text">
                    <tr>
                      <th className="py-2.5 px-3">#</th>
                      {Object.keys(quality.duplicate_summary.preview[0]).map((col) => (
                        <th key={col} className="py-2.5 px-3 whitespace-nowrap">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/40">
                    {quality.duplicate_summary.preview.map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-card-hover/60">
                        <td className="py-2 px-3 text-muted-text">{rIdx + 1}</td>
                        {Object.keys(row).map((col) => (
                          <td key={col} className="py-2 px-3 whitespace-nowrap text-primary-text">
                            {row[col] !== null ? String(row[col]) : "<null>"}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="bg-card border border-border rounded-xl p-8 text-center text-muted-text">
              <Copy className="w-8 h-8 text-success mx-auto mb-2" />
              <p className="text-sm font-medium text-primary-text">
                No duplicate rows detected.
              </p>
              <p className="text-xs text-muted-text mt-0.5">
                All records across the active dataset are unique.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Variance */}
      {activeTab === "variance" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-card border border-border rounded-xl p-5">
            <h3 className="text-sm font-semibold text-primary-text mb-2 flex items-center gap-1.5">
              <Sliders className="w-4 h-4 text-warning" />
              Constant (0-Variance) Columns
            </h3>
            <p className="text-xs text-muted-text mb-3">
              Fields containing exactly 1 distinct non-null value across all records.
            </p>
            <div className="space-y-2">
              {Object.keys(quality.variance_summary.constant_columns).length > 0 ? (
                Object.entries(quality.variance_summary.constant_columns).map(
                  ([col, val], idx) => (
                    <div
                      key={idx}
                      className="bg-background border border-border p-2.5 rounded text-xs font-mono"
                    >
                      <span className="font-semibold text-primary-text block">{col}</span>
                      <span className="text-muted-text text-[11px]">
                        Fixed value: &quot;{String(val)}&quot;
                      </span>
                    </div>
                  )
                )
              ) : (
                <span className="text-xs text-muted-text italic">
                  None detected. All columns have two or more unique values.
                </span>
              )}
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-5">
            <h3 className="text-sm font-semibold text-primary-text mb-2 flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4 text-danger" />
              Completely Empty Columns
            </h3>
            <p className="text-xs text-muted-text mb-3">
              Fields where 100% of cells are missing (null).
            </p>
            <div className="space-y-1.5">
              {quality.variance_summary.entirely_empty_columns.length > 0 ? (
                quality.variance_summary.entirely_empty_columns.map((col, idx) => (
                  <span
                    key={idx}
                    className="block bg-background border border-danger/30 text-danger px-2.5 py-1.5 rounded text-xs font-mono"
                  >
                    {col}
                  </span>
                ))
              ) : (
                <span className="text-xs text-muted-text italic">
                  None detected. All columns contain at least one valid cell.
                </span>
              )}
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-5">
            <h3 className="text-sm font-semibold text-primary-text mb-2 flex items-center gap-1.5">
              <HelpCircle className="w-4 h-4 text-amber-400" />
              Nearly-Empty Columns (&ge; 90% null)
            </h3>
            <p className="text-xs text-muted-text mb-3">
              Sparse fields where $\ge 90\%$ of rows contain null values.
            </p>
            <div className="space-y-1.5">
              {quality.variance_summary.nearly_empty_columns.length > 0 ? (
                quality.variance_summary.nearly_empty_columns.map((col, idx) => (
                  <span
                    key={idx}
                    className="block bg-background border border-amber-900/40 text-amber-300 px-2.5 py-1.5 rounded text-xs font-mono"
                  >
                    {col}
                  </span>
                ))
              ) : (
                <span className="text-xs text-muted-text italic">
                  None detected. All non-empty columns maintain sufficient data density.
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
