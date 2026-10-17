"use client";

import React from "react";
import {
  Search,
  Table,
  Binary,
  ShieldAlert,
  CopyX,
  Calculator,
  Target,
  GitFork,
  BarChart2,
  Download,
  FileSpreadsheet,
  CheckCircle2,
} from "lucide-react";

export default function CapabilitiesGrid() {
  const capabilities = [
    {
      title: "Inspect Datasets",
      description: "Examine dimensions, row/column counts, memory footprints, and total data cells with instantaneous profiling.",
      icon: Search,
      tag: "Overview",
    },
    {
      title: "Preview Rows & Columns",
      description: "Scroll through paginated, formatted dataset previews with column search and type tags.",
      icon: Table,
      tag: "Preview",
    },
    {
      title: "Understand Data Types",
      description: "Distinguish numeric, categorical, temporal, and boolean types with automatic disambiguation.",
      icon: Binary,
      tag: "Schema",
    },
    {
      title: "Audit Missing Values",
      description: "Detect null, empty, and NaN cells with column-by-column missing percentages and visual heatmaps.",
      icon: ShieldAlert,
      tag: "Quality",
    },
    {
      title: "Detect Duplicate Rows",
      description: "Isolate duplicate observations, compute exact duplication rates, and preview deduplicated records.",
      icon: CopyX,
      tag: "Integrity",
    },
    {
      title: "Descriptive Statistics",
      description: "Compute mean, median, standard deviation, quartiles, IQR, minimums, maximums, and frequency tables.",
      icon: Calculator,
      tag: "Statistics",
    },
    {
      title: "Discover Outliers",
      description: "Detect anomalies using Tukey's Interquartile Range (IQR) rule with an interactive sensitivity multiplier.",
      icon: Target,
      tag: "Outliers",
    },
    {
      title: "Study Correlations",
      description: "Generate Pearson, Spearman, or Kendall correlation matrices with interactive heatmaps.",
      icon: GitFork,
      tag: "Relationships",
    },
    {
      title: "Interactive Charts",
      description: "Render responsive Plotly visualizations including histograms, box plots, category bars, and distributions.",
      icon: BarChart2,
      tag: "Visuals",
    },
    {
      title: "Multi-Format Export",
      description: "Download Complete Analysis Archives (.ZIP), Excel Workbooks (.XLSX), JSON audit reports, and clean CSVs.",
      icon: Download,
      tag: "Export",
    },
  ];

  return (
    <section id="capabilities" className="py-12 max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
          What You Can Do with Analytix
        </h2>
        <p className="text-sm text-slate-600 max-w-xl mx-auto">
          Comprehensive data exploration capabilities designed for students, analysts, researchers, and engineers.
        </p>
      </div>

      {/* Grid of Capabilities */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {capabilities.map((cap, idx) => {
          const Icon = cap.icon;
          return (
            <div
              key={idx}
              className="bg-white/70 hover:bg-white border border-slate-200/80 hover:border-indigo-200 rounded-2xl p-5 shadow-sm transition-all hover:shadow-md space-y-2.5"
            >
              <div className="flex items-center justify-between">
                <div className="p-2 rounded-xl bg-slate-100 text-slate-800">
                  <Icon className="w-4 h-4 text-indigo-600" />
                </div>
                <span className="text-[10px] font-mono uppercase tracking-wider font-semibold bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
                  {cap.tag}
                </span>
              </div>
              <h3 className="text-sm font-bold text-slate-900">{cap.title}</h3>
              <p className="text-xs text-slate-600 leading-relaxed font-normal">
                {cap.description}
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
