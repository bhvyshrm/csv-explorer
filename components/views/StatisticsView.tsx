"use client";

import React, { useState } from "react";
import { AnalysisPayload } from "@/types/analytix";
import { Calculator, BookOpen, Layers } from "lucide-react";

interface StatisticsViewProps {
  data: AnalysisPayload;
}

export default function StatisticsView({ data }: StatisticsViewProps) {
  const [activeTab, setActiveTab] = useState<"numeric" | "categorical">("numeric");
  const [selectedCatCol, setSelectedCatCol] = useState<string>(
    data.overview.categorical_columns[0] || ""
  );

  const numericStats = data.numeric_statistics;
  const numColumns =
    numericStats.length > 0
      ? Object.keys(numericStats[0]).filter((k) => k !== "Metric")
      : [];

  const catColNames = data.overview.categorical_columns;
  const currentCatStat = selectedCatCol ? data.categorical_statistics[selectedCatCol] : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-card border border-border rounded-xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-primary-text flex items-center gap-2">
              <Calculator className="w-5 h-5 text-accent" />
              Descriptive Statistical Depth
            </h1>
            <p className="text-sm text-muted-text mt-0.5">
              Rigorous parametric, non-parametric, and categorical frequency calculations.
            </p>
          </div>

          <div className="flex border border-border rounded-lg overflow-hidden p-1 bg-background text-xs font-medium">
            <button
              onClick={() => setActiveTab("numeric")}
              className={`px-3 py-1.5 rounded transition-colors ${
                activeTab === "numeric"
                  ? "bg-accent text-white font-semibold"
                  : "text-muted-text hover:text-primary-text"
              }`}
            >
              Numeric Statistics ({numColumns.length})
            </button>
            <button
              onClick={() => setActiveTab("categorical")}
              className={`px-3 py-1.5 rounded transition-colors ${
                activeTab === "categorical"
                  ? "bg-accent text-white font-semibold"
                  : "text-muted-text hover:text-primary-text"
              }`}
            >
              Categorical Breakdown ({catColNames.length})
            </button>
          </div>
        </div>
      </div>

      {/* Educational Mentor Callouts */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
        <div className="bg-card border border-border/70 rounded-lg p-3">
          <div className="flex items-center gap-1.5 font-semibold text-accent mb-1">
            <BookOpen className="w-3.5 h-3.5" />
            Mean vs. Median
          </div>
          <p className="text-muted-text leading-relaxed">
            Mean is sensitive to extreme values. When Mean and Median diverge significantly, the distribution is skewed.
          </p>
        </div>

        <div className="bg-card border border-border/70 rounded-lg p-3">
          <div className="flex items-center gap-1.5 font-semibold text-accent-secondary mb-1">
            <BookOpen className="w-3.5 h-3.5" />
            Interquartile Range (IQR)
          </div>
          <p className="text-muted-text leading-relaxed">
            IQR = Q3 - Q1. Measures the central 50% spread resistant to outliers.
          </p>
        </div>

        <div className="bg-card border border-border/70 rounded-lg p-3">
          <div className="flex items-center gap-1.5 font-semibold text-blue-400 mb-1">
            <BookOpen className="w-3.5 h-3.5" />
            Sample Variance (ddof=1)
          </div>
          <p className="text-muted-text leading-relaxed">
            Computes Bessel-corrected unbiased variance. Undefined on single-observation columns.
          </p>
        </div>

        <div className="bg-card border border-border/70 rounded-lg p-3">
          <div className="flex items-center gap-1.5 font-semibold text-purple-400 mb-1">
            <BookOpen className="w-3.5 h-3.5" />
            Distribution Skewness
          </div>
          <p className="text-muted-text leading-relaxed">
            Fisher-Pearson skewness: positive indicates a right tail; negative indicates a left tail.
          </p>
        </div>
      </div>

      {/* Numeric Tab */}
      {activeTab === "numeric" && (
        <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
          {numColumns.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-background/90 border-b border-border uppercase tracking-wider text-muted-text">
                  <tr>
                    <th className="py-3 px-4 font-bold text-accent sticky left-0 bg-background/95 border-r border-border/60">
                      Metric
                    </th>
                    {numColumns.map((col) => (
                      <th key={col} className="py-3 px-4 text-right text-primary-text">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/40">
                  {numericStats.map((row, idx) => (
                    <tr key={idx} className="hover:bg-card-hover/60 transition-colors">
                      <td className="py-2.5 px-4 font-semibold text-primary-text sticky left-0 bg-card border-r border-border/60">
                        {row.Metric}
                      </td>
                      {numColumns.map((col) => {
                        const val = row[col];
                        return (
                          <td key={col} className="py-2.5 px-4 text-right text-primary-text">
                            {val !== null && val !== undefined
                              ? typeof val === "number"
                                ? val.toLocaleString(undefined, {
                                    maximumFractionDigits: 4,
                                  })
                                : String(val)
                              : "-"}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center text-sm text-muted-text">
              No numeric columns present in the active dataset.
            </div>
          )}
        </div>
      )}

      {/* Categorical Tab */}
      {activeTab === "categorical" && (
        <div className="space-y-4">
          {catColNames.length > 0 ? (
            <>
              {/* Column Selector */}
              <div className="bg-card border border-border rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-accent" />
                  <span className="text-sm font-semibold text-primary-text">
                    Select Categorical Column:
                  </span>
                </div>
                <select
                  value={selectedCatCol}
                  onChange={(e) => setSelectedCatCol(e.target.value)}
                  className="bg-background border border-border focus:border-accent text-primary-text text-sm rounded px-3 py-1.5 outline-none font-mono cursor-pointer"
                >
                  {catColNames.map((name) => (
                    <option key={name} value={name}>
                      {name}
                    </option>
                  ))}
                </select>
              </div>

              {currentCatStat && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Summary Card */}
                  <div className="bg-card border border-border rounded-xl p-5 space-y-4">
                    <h3 className="text-sm font-semibold text-primary-text">
                      Column Cardinality
                    </h3>
                    <div className="space-y-3 font-mono text-xs">
                      <div className="bg-background p-3 rounded border border-border/70">
                        <span className="text-muted-text block text-[10px] uppercase">
                          Unique Classes
                        </span>
                        <span className="text-xl font-bold text-accent">
                          {currentCatStat.unique_count.toLocaleString()}
                        </span>
                      </div>
                      <div className="bg-background p-3 rounded border border-border/70">
                        <span className="text-muted-text block text-[10px] uppercase">
                          Mode (Most Frequent)
                        </span>
                        <span className="text-sm font-bold text-primary-text truncate block mt-0.5">
                          {currentCatStat.most_frequent_value || "-"}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Frequency Distribution Table */}
                  <div className="md:col-span-2 bg-card border border-border rounded-xl overflow-hidden">
                    <div className="px-5 py-3 border-b border-border font-semibold text-sm text-primary-text">
                      Frequency Distribution & Percentages
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs font-mono">
                        <thead className="bg-background/80 border-b border-border uppercase text-muted-text">
                          <tr>
                            <th className="py-2.5 px-4">Category</th>
                            <th className="py-2.5 px-4 text-right">Frequency</th>
                            <th className="py-2.5 px-4 text-right">Share (%)</th>
                            <th className="py-2.5 px-4 w-40">Proportion</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border/40">
                          {currentCatStat.frequency_table.map((row, idx) => (
                            <tr key={idx} className="hover:bg-card-hover/60">
                              <td className="py-2.5 px-4 font-semibold text-primary-text truncate max-w-xs">
                                {row.Category}
                              </td>
                              <td className="py-2.5 px-4 text-right text-primary-text">
                                {row.Count.toLocaleString()}
                              </td>
                              <td className="py-2.5 px-4 text-right text-accent font-semibold">
                                {row.Percentage.toFixed(1)}%
                              </td>
                              <td className="py-2.5 px-4">
                                <div className="w-full bg-background rounded-full h-2 overflow-hidden border border-border/80">
                                  <div
                                    className="h-full bg-accent rounded-full"
                                    style={{ width: `${Math.min(row.Percentage, 100)}%` }}
                                  />
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="bg-card border border-border rounded-xl p-8 text-center text-sm text-muted-text">
              No categorical columns detected in the active dataset.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
