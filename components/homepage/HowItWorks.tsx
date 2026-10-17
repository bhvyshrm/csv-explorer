"use client";

import React from "react";
import { Upload, BarChart2, Download, ArrowRight } from "lucide-react";

export default function HowItWorks() {
  const steps = [
    {
      num: "01",
      title: "Upload your file",
      description: "Drop your CSV, Excel workbook, JSON, Parquet, TSV, or Log file into the browser. Files up to 4.5 MB are supported.",
      icon: Upload,
      color: "from-indigo-500 to-indigo-600",
    },
    {
      num: "02",
      title: "Explore & analyze in memory",
      description: "Analytix instantly calculates data health scores, missing value breakdowns, descriptive statistics, and Plotly charts.",
      icon: BarChart2,
      color: "from-purple-500 to-purple-600",
    },
    {
      num: "03",
      title: "Export your insights",
      description: "Download a Complete Analysis Archive (.ZIP), multi-sheet Excel Workbook (.XLSX), clean CSV tables, or JSON reports.",
      icon: Download,
      color: "from-teal-500 to-emerald-600",
    },
  ];

  return (
    <section id="how-it-works" className="py-12 max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
          How It Works
        </h2>
        <p className="text-sm text-slate-600 max-w-xl mx-auto">
          From raw data to publication-ready analysis reports in three simple steps.
        </p>
      </div>

      {/* 3 Step Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          return (
            <div
              key={idx}
              className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-3xl p-6 shadow-sm hover:shadow-md transition-all relative space-y-4"
            >
              <div className="flex items-center justify-between">
                <span className="text-2xl font-extrabold font-mono text-slate-300">
                  {step.num}
                </span>
                <div
                  className={`w-10 h-10 rounded-2xl bg-gradient-to-tr ${step.color} text-white flex items-center justify-center shadow-sm`}
                >
                  <Icon className="w-5 h-5" />
                </div>
              </div>

              <div>
                <h3 className="text-base font-bold text-slate-900 mb-1.5">{step.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed font-normal">
                  {step.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
