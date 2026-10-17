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
      <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-3xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs uppercase tracking-wider font-semibold text-indigo-700 bg-indigo-50 border border-indigo-200 px-2.5 py-0.5 rounded-full font-mono">
                Statistical Depth
              </span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
              <Calculator className="w-5 h-5 text-indigo-600" />
              Descriptive Statistics
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Rigorous parametric, non-parametric, and categorical frequency calculations.
            </p>
          </div>

          <div className="flex border border-slate-200 rounded-xl overflow-hidden p-1 bg-slate-100/80 text-xs font-medium self-start md:self-auto">
            <button
              onClick={() => setActiveTab("numeric")}
              className={`px-3.5 py-2 rounded-lg transition-all ${
                activeTab === "numeric"
                  ? "bg-white text-indigo-700 shadow-sm font-semibold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Numeric Statistics ({numColumns.length})
            </button>
            <button
              onClick={() => setActiveTab("categorical")}
              className={`px-3.5 py-2 rounded-lg transition-all ${
                activeTab === "categorical"
                  ? "bg-white text-indigo-700 shadow-sm font-semibold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Categorical Breakdown ({catColNames.length})
            </button>
          </div>
        </div>
      </div>

      {/* Educational Mentor Callouts */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
        <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center gap-1.5 font-semibold text-indigo-700 mb-1.5">
            <BookOpen className="w-4 h-4 text-indigo-600" />
            Mean vs. Median
          </div>
          <p className="text-slate-600 leading-relaxed">
            Mean is sensitive to extreme values. When Mean and Median diverge significantly, the distribution is skewed.
          </p>
        </div>

        <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center gap-1.5 font-semibold text-teal-700 mb-1.5">
            <BookOpen className="w-4 h-4 text-teal-600" />
            Interquartile Range (IQR)
          </div>
          <p className="text-slate-600 leading-relaxed">
            IQR = Q3 - Q1. Measures the central 50% spread resistant to outliers.
          </p>
        </div>

        <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center gap-1.5 font-semibold text-blue-700 mb-1.5">
            <BookOpen className="w-4 h-4 text-blue-600" />
            Sample Variance (ddof=1)
          </div>
          <p className="text-slate-600 leading-relaxed">
            Computes Bessel-corrected unbiased variance. Undefined on single-observation columns.
          </p>
        </div>

        <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center gap-1.5 font-semibold text-purple-700 mb-1.5">
            <BookOpen className="w-4 h-4 text-purple-600" />
            Distribution Skewness
          </div>
          <p className="text-slate-600 leading-relaxed">
            Fisher-Pearson skewness: positive indicates a right tail; negative indicates a left tail.
          </p>
        </div>
      </div>

      {/* Numeric Tab */}
      {activeTab === "numeric" && (
        <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-3xl overflow-hidden shadow-sm">
          {numColumns.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-50/90 border-b border-slate-200 uppercase tracking-wider text-slate-600">
                  <tr>
                    <th className="py-3 px-4 font-bold text-indigo-700 sticky left-0 bg-slate-50/95 border-r border-slate-200">
                      Metric
                    </th>
                    {numColumns.map((col) => (
                      <th key={col} className="py-3 px-4 text-right text-slate-900 font-semibold">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {numericStats.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-2.5 px-4 font-semibold text-slate-900 sticky left-0 bg-white/95 border-r border-slate-200">
                        {row.Metric}
                      </td>
                      {numColumns.map((col) => {
                        const val = row[col];
                        return (
                          <td key={col} className="py-2.5 px-4 text-right text-slate-800">
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
            <div className="p-8 text-center text-sm text-slate-500">
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
              <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm">
                <div className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-indigo-600" />
                  <span className="text-sm font-semibold text-slate-900">
                    Select Categorical Column:
                  </span>
                </div>
                <select
                  value={selectedCatCol}
                  onChange={(e) => setSelectedCatCol(e.target.value)}
                  className="bg-white border border-slate-200 focus:border-indigo-500 text-slate-900 text-sm rounded-lg px-3 py-1.5 outline-none font-mono cursor-pointer shadow-sm"
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
                  <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-2xl p-5 space-y-4 shadow-sm">
                    <h3 className="text-sm font-semibold text-slate-900">
                      Column Cardinality
                    </h3>
                    <div className="space-y-3 font-mono text-xs">
                      <div className="bg-slate-50/80 p-3.5 rounded-xl border border-slate-200/70">
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">
                          Unique Classes
                        </span>
                        <span className="text-xl font-bold text-indigo-700">
                          {currentCatStat.unique_count.toLocaleString()}
                        </span>
                      </div>
                      <div className="bg-slate-50/80 p-3.5 rounded-xl border border-slate-200/70">
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">
                          Mode (Most Frequent)
                        </span>
                        <span className="text-sm font-bold text-slate-900 truncate block mt-0.5">
                          {currentCatStat.most_frequent_value || "-"}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Frequency Distribution Table */}
                  <div className="md:col-span-2 bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-2xl overflow-hidden shadow-sm">
                    <div className="px-5 py-3 border-b border-slate-200 font-semibold text-sm text-slate-900 bg-slate-50/60">
                      Frequency Distribution &amp; Percentages
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs font-mono">
                        <thead className="bg-slate-50/90 border-b border-slate-200 uppercase text-slate-600">
                          <tr>
                            <th className="py-2.5 px-4 font-semibold">Category</th>
                            <th className="py-2.5 px-4 text-right font-semibold">Frequency</th>
                            <th className="py-2.5 px-4 text-right font-semibold">Share (%)</th>
                            <th className="py-2.5 px-4 w-40 font-semibold">Proportion</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {currentCatStat.frequency_table.map((row, idx) => (
                            <tr key={idx} className="hover:bg-slate-50/70 transition-colors">
                              <td className="py-2.5 px-4 font-semibold text-slate-900 truncate max-w-xs">
                                {row.Category}
                              </td>
                              <td className="py-2.5 px-4 text-right text-slate-800">
                                {row.Count.toLocaleString()}
                              </td>
                              <td className="py-2.5 px-4 text-right text-indigo-700 font-semibold">
                                {row.Percentage.toFixed(1)}%
                              </td>
                              <td className="py-2.5 px-4">
                                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200/80">
                                  <div
                                    className="h-full bg-indigo-600 rounded-full"
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
            <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-2xl p-8 text-center text-sm text-slate-500 shadow-sm">
              No categorical columns detected in the active dataset.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
