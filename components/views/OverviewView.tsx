"use client";

import React from "react";
import { AnalysisPayload } from "@/types/analytix";
import {
  Layers,
  Columns,
  Hash,
  Database,
  Copy,
  Activity,
  Calendar,
  ToggleLeft,
  FileSpreadsheet,
} from "lucide-react";

interface OverviewViewProps {
  data: AnalysisPayload;
}

export default function OverviewView({ data }: OverviewViewProps) {
  const { overview, quality } = data;

  const metricCards = [
    {
      label: "Total Rows",
      value: overview.total_rows.toLocaleString(),
      icon: Layers,
      color: "text-accent",
      subtext: `${overview.total_cells.toLocaleString()} total data cells`,
    },
    {
      label: "Total Columns",
      value: overview.total_columns.toLocaleString(),
      icon: Columns,
      color: "text-accent-secondary",
      subtext: `${overview.numeric_columns.length} numeric, ${overview.categorical_columns.length} categorical`,
    },
    {
      label: "Memory Footprint",
      value: overview.memory_usage_formatted,
      icon: Database,
      color: "text-blue-400",
      subtext: `${overview.memory_usage_bytes.toLocaleString()} bytes in memory`,
    },
    {
      label: "Duplicate Rows",
      value: overview.total_duplicate_rows.toLocaleString(),
      icon: Copy,
      color: overview.total_duplicate_rows > 0 ? "text-warning" : "text-success",
      subtext: `${overview.duplicate_rows_pct.toFixed(1)}% duplication rate`,
    },
    {
      label: "Data Quality Score",
      value: `${quality.overall_health_score.toFixed(0)}/100`,
      icon: Activity,
      color:
        quality.overall_health_score >= 85
          ? "text-success"
          : quality.overall_health_score >= 65
          ? "text-warning"
          : "text-danger",
      subtext: quality.status,
    },
  ];

  const typeClassifications = [
    {
      label: "Numeric",
      count: overview.numeric_columns.length,
      icon: Hash,
      color: "bg-purple-50 text-purple-700 border-purple-200",
      list: overview.numeric_columns,
    },
    {
      label: "Categorical",
      count: overview.categorical_columns.length,
      icon: FileSpreadsheet,
      color: "bg-teal-50 text-teal-700 border-teal-200",
      list: overview.categorical_columns,
    },
    {
      label: "Datetime",
      count: overview.datetime_columns.length,
      icon: Calendar,
      color: "bg-blue-50 text-blue-700 border-blue-200",
      list: overview.datetime_columns,
    },
    {
      label: "Boolean",
      count: overview.boolean_columns.length,
      icon: ToggleLeft,
      color: "bg-indigo-50 text-indigo-700 border-indigo-200",
      list: overview.boolean_columns,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-3xl p-6 shadow-sm relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs uppercase tracking-wider font-semibold text-indigo-700 bg-indigo-50 border border-indigo-200 px-2.5 py-0.5 rounded-full font-mono">
                Active Dataset
              </span>
              <span className="text-xs text-slate-500 font-mono">
                {data.dataset_format}
              </span>
              {data.active_worksheet && (
                <span className="text-xs bg-slate-100 border border-slate-200 px-2.5 py-0.5 rounded-full text-slate-800 font-mono">
                  Sheet: {data.active_worksheet}
                </span>
              )}
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              {data.dataset_name}
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Deterministic in-memory profiling, quality diagnostics, and structural breakdown.
            </p>
          </div>
        </div>
      </div>

      {/* Top 5 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {metricCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              className="bg-white/80 backdrop-blur-md border border-slate-200/80 hover:border-indigo-300 transition-colors rounded-2xl p-5 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-500 uppercase tracking-wider font-mono">
                  {card.label}
                </span>
                <Icon className={`w-4 h-4 ${card.color}`} />
              </div>
              <div className="text-2xl font-bold text-slate-900 mt-2 font-mono">
                {card.value}
              </div>
              <p className="text-xs text-slate-500 mt-1 truncate">
                {card.subtext}
              </p>
            </div>
          );
        })}
      </div>

      {/* Semantic Column Breakdown */}
      <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-3xl p-6 shadow-sm">
        <h2 className="text-base font-semibold text-slate-900 mb-4 flex items-center gap-2">
          <Columns className="w-4 h-4 text-indigo-600" />
          Semantic Column Classifications
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {typeClassifications.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                className="bg-slate-50/70 border border-slate-200/80 rounded-2xl p-4 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-slate-800 flex items-center gap-1.5">
                      <Icon className="w-4 h-4 text-slate-500" />
                      {item.label}
                    </span>
                    <span className={`text-xs px-2.5 py-0.5 rounded-full font-mono border ${item.color}`}>
                      {item.count} cols
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5 mt-3 max-h-36 overflow-y-auto">
                    {item.list.length > 0 ? (
                      item.list.map((colName, cIdx) => (
                        <span
                          key={cIdx}
                          className="text-xs bg-white border border-slate-200 text-slate-700 px-2 py-1 rounded-lg font-mono shadow-xs"
                        >
                          {colName}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-400 italic">None detected</span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
