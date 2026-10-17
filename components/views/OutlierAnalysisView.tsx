"use client";

import React, { useState } from "react";
import { AnalysisPayload, OutlierResult } from "@/types/analytix";
import { Target, Download, Sliders, AlertTriangle } from "lucide-react";

interface OutlierAnalysisViewProps {
  data: AnalysisPayload;
  onRecalculateOutliers: (column: string, multiplier: number) => Promise<OutlierResult | null>;
}

export default function OutlierAnalysisView({
  data,
  onRecalculateOutliers,
}: OutlierAnalysisViewProps) {
  const numCols = data.overview.numeric_columns;
  const [selectedCol, setSelectedCol] = useState<string>(numCols[0] || "");
  const [multiplier, setMultiplier] = useState<number>(1.5);
  const [activeOutlierResult, setActiveOutlierResult] = useState<OutlierResult | null>(
    selectedCol && data.outliers[selectedCol] ? data.outliers[selectedCol] : null
  );
  const [isCalculating, setIsCalculating] = useState(false);

  const handleColumnChange = async (colName: string) => {
    setSelectedCol(colName);
    const existing = data.outliers[colName];
    if (existing && existing.multiplier === multiplier) {
      setActiveOutlierResult(existing);
    } else {
      setIsCalculating(true);
      const res = await onRecalculateOutliers(colName, multiplier);
      setActiveOutlierResult(res);
      setIsCalculating(false);
    }
  };

  const handleMultiplierChange = async (newMultiplier: number) => {
    setMultiplier(newMultiplier);
    if (!selectedCol) return;
    setIsCalculating(true);
    const res = await onRecalculateOutliers(selectedCol, newMultiplier);
    setActiveOutlierResult(res);
    setIsCalculating(false);
  };

  const handleExportOutliersCSV = () => {
    if (!activeOutlierResult || activeOutlierResult.flagged_preview.length === 0) return;
    const cols = Object.keys(activeOutlierResult.flagged_preview[0]);
    const headers = cols.map((c) => `"${c}"`).join(",");
    const rows = activeOutlierResult.flagged_preview.map((r) =>
      cols
        .map((c) => {
          const val = r[c];
          if (val === null || val === undefined) return "";
          return `"${String(val).replace(/"/g, '""')}"`;
        })
        .join(",")
    );
    const csvContent = [headers, ...rows].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${data.dataset_name}_${selectedCol}_outliers.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (numCols.length === 0) {
    return (
      <div className="bg-card border border-border rounded-xl p-8 text-center text-muted-text">
        <Target className="w-10 h-10 text-muted-text mx-auto mb-2" />
        <h2 className="text-base font-semibold text-primary-text">
          No Numeric Columns Available
        </h2>
        <p className="text-xs text-muted-text mt-1">
          IQR outlier detection requires at least one numeric feature in the active dataset.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-3xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <Target className="w-5 h-5 text-indigo-600" />
              Mathematical Outlier Detection (Tukey IQR)
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Identifies values beyond statistical thresholds: [Q1 - k &times; IQR, Q3 + k &times; IQR].
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Column Selector */}
            <div className="flex items-center gap-2 bg-background border border-border rounded-lg px-3 py-1.5 text-xs">
              <span className="text-muted-text font-mono">Column:</span>
              <select
                value={selectedCol}
                onChange={(e) => handleColumnChange(e.target.value)}
                className="bg-card border border-border focus:border-accent text-primary-text rounded px-2 py-1 outline-none font-mono cursor-pointer"
              >
                {numCols.map((col) => (
                  <option key={col} value={col}>
                    {col}
                  </option>
                ))}
              </select>
            </div>

            {/* Multiplier Slider Toggle */}
            <div className="flex items-center gap-1.5 bg-background border border-border rounded-lg p-1 text-xs">
              <Sliders className="w-3.5 h-3.5 text-muted-text ml-1" />
              <button
                onClick={() => handleMultiplierChange(1.5)}
                className={`px-2.5 py-1 rounded font-mono text-xs transition-colors ${
                  multiplier === 1.5
                    ? "bg-accent text-white font-semibold"
                    : "text-muted-text hover:text-primary-text"
                }`}
              >
                1.5&times; (Standard)
              </button>
              <button
                onClick={() => handleMultiplierChange(3.0)}
                className={`px-2.5 py-1 rounded font-mono text-xs transition-colors ${
                  multiplier === 3.0
                    ? "bg-accent text-white font-semibold"
                    : "text-muted-text hover:text-primary-text"
                }`}
              >
                3.0&times; (Extreme)
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Outlier Metrics Cards */}
      {activeOutlierResult ? (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 font-mono text-xs">
            <div className="bg-card border border-border rounded-xl p-4">
              <span className="text-muted-text block text-[10px] uppercase">
                Q1 (25th %)
              </span>
              <span className="text-base font-bold text-primary-text mt-1 block">
                {activeOutlierResult.q1 !== null
                  ? activeOutlierResult.q1.toLocaleString(undefined, { maximumFractionDigits: 2 })
                  : "-"}
              </span>
            </div>

            <div className="bg-card border border-border rounded-xl p-4">
              <span className="text-muted-text block text-[10px] uppercase">
                Q3 (75th %)
              </span>
              <span className="text-base font-bold text-primary-text mt-1 block">
                {activeOutlierResult.q3 !== null
                  ? activeOutlierResult.q3.toLocaleString(undefined, { maximumFractionDigits: 2 })
                  : "-"}
              </span>
            </div>

            <div className="bg-card border border-border rounded-xl p-4">
              <span className="text-muted-text block text-[10px] uppercase">
                IQR (Spread)
              </span>
              <span className="text-base font-bold text-accent-secondary mt-1 block">
                {activeOutlierResult.iqr !== null
                  ? activeOutlierResult.iqr.toLocaleString(undefined, { maximumFractionDigits: 2 })
                  : "-"}
              </span>
            </div>

            <div className="bg-card border border-border rounded-xl p-4">
              <span className="text-muted-text block text-[10px] uppercase">
                Lower Bound
              </span>
              <span className="text-base font-bold text-blue-400 mt-1 block truncate">
                {activeOutlierResult.lower_bound !== null
                  ? activeOutlierResult.lower_bound.toLocaleString(undefined, { maximumFractionDigits: 2 })
                  : "-"}
              </span>
            </div>

            <div className="bg-card border border-border rounded-xl p-4">
              <span className="text-muted-text block text-[10px] uppercase">
                Upper Bound
              </span>
              <span className="text-base font-bold text-purple-400 mt-1 block truncate">
                {activeOutlierResult.upper_bound !== null
                  ? activeOutlierResult.upper_bound.toLocaleString(undefined, { maximumFractionDigits: 2 })
                  : "-"}
              </span>
            </div>

            <div className="bg-card border border-border rounded-xl p-4">
              <span className="text-muted-text block text-[10px] uppercase">
                Flagged Outliers
              </span>
              <span
                className={`text-base font-bold mt-1 block ${
                  activeOutlierResult.flagged_count > 0 ? "text-warning" : "text-success"
                }`}
              >
                {activeOutlierResult.flagged_count} ({activeOutlierResult.flagged_pct.toFixed(1)}%)
              </span>
            </div>
          </div>

          {/* Flagged Outlier Records Table */}
          <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
            <div className="p-4 border-b border-border flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-warning" />
                <h3 className="text-sm font-semibold text-primary-text">
                  Flagged Records Preview ({activeOutlierResult.flagged_count} total detected)
                </h3>
              </div>

              {activeOutlierResult.flagged_count > 0 && (
                <button
                  onClick={handleExportOutliersCSV}
                  className="flex items-center gap-2 bg-card-hover border border-border hover:border-accent text-primary-text px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                >
                  <Download className="w-3.5 h-3.5 text-accent" />
                  Export Outliers (CSV)
                </button>
              )}
            </div>

            {activeOutlierResult.flagged_preview.length > 0 ? (
              <div className="overflow-x-auto max-h-96">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-background/90 sticky top-0 border-b border-border uppercase text-muted-text">
                    <tr>
                      <th className="py-2.5 px-3">#</th>
                      {Object.keys(activeOutlierResult.flagged_preview[0]).map((col) => (
                        <th
                          key={col}
                          className={`py-2.5 px-3 whitespace-nowrap ${
                            col === selectedCol ? "text-warning font-bold" : ""
                          }`}
                        >
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/40">
                    {activeOutlierResult.flagged_preview.map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-card-hover/60">
                        <td className="py-2 px-3 text-muted-text">{rIdx + 1}</td>
                        {Object.keys(row).map((col) => {
                          const isTarget = col === selectedCol;
                          return (
                            <td
                              key={col}
                              className={`py-2 px-3 whitespace-nowrap ${
                                isTarget
                                  ? "text-warning font-bold bg-warning/5"
                                  : "text-primary-text"
                              }`}
                            >
                              {row[col] !== null ? String(row[col]) : "<null>"}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-muted-text">
                No observations fall outside the [{activeOutlierResult.lower_bound?.toFixed(1)}, {activeOutlierResult.upper_bound?.toFixed(1)}] range at {multiplier}&times; IQR.
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="p-8 text-center text-sm text-muted-text">
          Calculating statistical boundaries...
        </div>
      )}
    </div>
  );
}
