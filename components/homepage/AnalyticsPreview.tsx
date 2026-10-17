"use client";

import React from "react";
import {
  BarChart2,
  Download,
  ShieldCheck,
  Table,
  Layers,
  ArrowRight,
  TrendingUp,
} from "lucide-react";

interface AnalyticsPreviewProps {
  onStartExploring: () => void;
}

export default function AnalyticsPreview({ onStartExploring }: AnalyticsPreviewProps) {
  return (
    <section className="py-12 max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-1.5 bg-indigo-50 border border-indigo-200/80 rounded-full px-3 py-1 text-[11px] font-mono text-indigo-700 font-medium">
          <span>Workflow Demonstration</span>
        </div>
        <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
          Comprehensive Analysis Workflow
        </h2>
        <p className="text-sm text-slate-600 max-w-xl mx-auto">
          See how Analytix transforms unstructured records into actionable insights and downloadable reports.
        </p>
      </div>

      {/* Main Glass Preview Card */}
      <div className="bg-white/85 backdrop-blur-xl border border-white/90 rounded-3xl p-6 sm:p-8 shadow-glass-card space-y-6">
        {/* Top bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-200/70 gap-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-xs">
              CSV
            </div>
            <div>
              <div className="font-bold text-slate-900 text-sm">sample_superstore_eda.csv</div>
              <div className="text-[11px] text-slate-500 font-mono">
                1,420 rows • 18 columns • 284 KB in memory
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs bg-emerald-50 text-emerald-700 border border-emerald-200/80 px-2.5 py-1 rounded-full font-semibold flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" />
              Quality: 96/100
            </span>
            <button
              onClick={onStartExploring}
              className="flex items-center gap-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs px-3.5 py-1.5 rounded-full font-medium transition-all shadow-xs"
            >
              <span>Explore Live</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>

        {/* 3 Analytics Columns */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Column 1: Descriptive Stats */}
          <div className="bg-slate-50/90 rounded-2xl p-4 border border-slate-100 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono">
                Sales Distribution
              </span>
              <TrendingUp className="w-4 h-4 text-indigo-600" />
            </div>
            <div className="space-y-1.5 text-xs font-mono">
              <div className="flex justify-between py-1 border-b border-slate-200/60">
                <span className="text-slate-500">Mean:</span>
                <span className="font-semibold text-slate-800">$238.45</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-200/60">
                <span className="text-slate-500">Median:</span>
                <span className="font-semibold text-slate-800">$54.90</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-200/60">
                <span className="text-slate-500">Std Dev:</span>
                <span className="font-semibold text-slate-800">$586.20</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-500">IQR Outliers:</span>
                <span className="font-semibold text-amber-600">14 flagged (1.0%)</span>
              </div>
            </div>
          </div>

          {/* Column 2: Data Quality Breakdown */}
          <div className="bg-slate-50/90 rounded-2xl p-4 border border-slate-100 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono">
                Quality Audit
              </span>
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="space-y-2 text-xs">
              <div className="bg-white p-2.5 rounded-xl border border-slate-200/60 flex items-center justify-between">
                <div>
                  <div className="font-semibold text-slate-800 text-[11px]">Duplicate Rows</div>
                  <div className="text-[10px] text-slate-500 font-mono">0 rows identified</div>
                </div>
                <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded text-[10px] font-bold">
                  PASS
                </span>
              </div>
              <div className="bg-white p-2.5 rounded-xl border border-slate-200/60 flex items-center justify-between">
                <div>
                  <div className="font-semibold text-slate-800 text-[11px]">Postal Code Nulls</div>
                  <div className="text-[10px] text-slate-500 font-mono">11 missing values (0.8%)</div>
                </div>
                <span className="text-amber-700 bg-amber-50 px-2 py-0.5 rounded text-[10px] font-bold">
                  NOTICE
                </span>
              </div>
            </div>
          </div>

          {/* Column 3: Ready Export Packages */}
          <div className="bg-slate-50/90 rounded-2xl p-4 border border-slate-100 space-y-3 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono">
                  Export Reports
                </span>
                <Download className="w-4 h-4 text-indigo-600" />
              </div>
              <p className="text-[11px] text-slate-500 leading-normal">
                Generate complete analysis packages with one click.
              </p>
            </div>

            <div className="space-y-2">
              <div className="bg-white p-2.5 rounded-xl border border-slate-200/60 flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-700 text-[11px]">Complete Report (.ZIP)</span>
                <span className="text-[10px] font-mono text-indigo-600 font-bold">All Formats</span>
              </div>
              <div className="bg-white p-2.5 rounded-xl border border-slate-200/60 flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-700 text-[11px]">Excel Workbook (.XLSX)</span>
                <span className="text-[10px] font-mono text-emerald-600 font-bold">Multi-Tab</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
