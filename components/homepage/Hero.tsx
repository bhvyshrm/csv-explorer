"use client";

import React from "react";
import {
  ArrowRight,
  Sparkles,
  ShieldCheck,
  BarChart3,
  Layers,
  Database,
  CheckCircle2,
  Table,
} from "lucide-react";

interface HeroProps {
  onStartExploring: () => void;
  onExploreFeatures: () => void;
}

export default function Hero({ onStartExploring, onExploreFeatures }: HeroProps) {
  return (
    <section id="hero" className="py-12 md:py-16 text-center max-w-4xl mx-auto space-y-8">
      {/* Badge */}
      <div className="inline-flex items-center gap-2 bg-white/80 border border-slate-200/90 rounded-full px-4 py-1.5 shadow-sm text-xs text-slate-700 font-medium animate-fade-in">
        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        <span>Powerful data exploration and reporting, free to use</span>
      </div>

      {/* Main Headline */}
      <div className="space-y-4">
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.12]">
          Your data has a story. <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-teal-500 bg-clip-text text-transparent">
            Let's discover it.
          </span>
        </h1>
        <p className="text-base sm:text-lg md:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed font-normal">
          Explore datasets, uncover patterns, understand data quality, and turn raw files into clear insights — all in one simple workspace.
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
        <button
          onClick={onStartExploring}
          className="w-full sm:w-auto flex items-center justify-center gap-2.5 bg-slate-900 hover:bg-slate-800 text-white px-7 py-3.5 rounded-full text-sm font-semibold shadow-md hover:shadow-lg transition-all group"
        >
          <span>Start Exploring</span>
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </button>

        <button
          onClick={onExploreFeatures}
          className="w-full sm:w-auto flex items-center justify-center gap-2 bg-white/80 hover:bg-white text-slate-700 hover:text-slate-900 border border-slate-200/80 px-6 py-3.5 rounded-full text-sm font-medium shadow-sm transition-all"
        >
          <span>Explore Capabilities</span>
        </button>
      </div>

      {/* Honest Supporting Tag */}
      <p className="text-xs text-slate-500 font-normal">
        Free to use • No coding required for supported analyses • 100% in-memory processing
      </p>

      {/* Realistic Interactive Demo Preview Visual */}
      <div className="pt-6">
        <div className="bg-white/80 backdrop-blur-md border border-white/90 rounded-2xl p-5 shadow-glass-card max-w-3xl mx-auto text-left space-y-4">
          {/* Top Bar of Preview */}
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 text-xs">
            <div className="flex items-center gap-2 font-mono">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
              <span className="font-semibold text-slate-800">sample_superstore_eda.csv</span>
              <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded text-[10px]">CSV</span>
            </div>
            <span className="text-[11px] text-slate-400 font-mono italic">Demo Preview Dataset</span>
          </div>

          {/* Mini KPI row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-50/80 rounded-xl p-3 border border-slate-100">
              <div className="text-[11px] uppercase tracking-wider text-slate-500 font-semibold">Total Rows</div>
              <div className="text-xl font-bold text-slate-900 mt-0.5">1,420</div>
            </div>
            <div className="bg-slate-50/80 rounded-xl p-3 border border-slate-100">
              <div className="text-[11px] uppercase tracking-wider text-slate-500 font-semibold">Columns</div>
              <div className="text-xl font-bold text-slate-900 mt-0.5">18</div>
            </div>
            <div className="bg-emerald-50/70 rounded-xl p-3 border border-emerald-100/60">
              <div className="text-[11px] uppercase tracking-wider text-emerald-700 font-semibold">Health Score</div>
              <div className="text-xl font-bold text-emerald-800 mt-0.5">96 / 100</div>
            </div>
            <div className="bg-purple-50/70 rounded-xl p-3 border border-purple-100/60">
              <div className="text-[11px] uppercase tracking-wider text-purple-700 font-semibold">Missing Cells</div>
              <div className="text-xl font-bold text-purple-800 mt-0.5">0.4%</div>
            </div>
          </div>

          {/* Mini Table Preview */}
          <div className="overflow-x-auto rounded-xl border border-slate-100 text-xs">
            <table className="w-full text-left font-mono">
              <thead className="bg-slate-50/90 text-slate-600 border-b border-slate-100">
                <tr>
                  <th className="py-2 px-3">Order_ID</th>
                  <th className="py-2 px-3">Category</th>
                  <th className="py-2 px-3">Sub_Category</th>
                  <th className="py-2 px-3">Sales ($)</th>
                  <th className="py-2 px-3">Profit ($)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                <tr>
                  <td className="py-1.5 px-3 text-indigo-600 font-medium">CA-2024-152156</td>
                  <td className="py-1.5 px-3">Furniture</td>
                  <td className="py-1.5 px-3">Bookcases</td>
                  <td className="py-1.5 px-3 font-semibold">$261.96</td>
                  <td className="py-1.5 px-3 text-emerald-600">+$41.91</td>
                </tr>
                <tr>
                  <td className="py-1.5 px-3 text-indigo-600 font-medium">CA-2024-138688</td>
                  <td className="py-1.5 px-3">Technology</td>
                  <td className="py-1.5 px-3">Phones</td>
                  <td className="py-1.5 px-3 font-semibold">$731.94</td>
                  <td className="py-1.5 px-3 text-emerald-600">+$219.58</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
}
