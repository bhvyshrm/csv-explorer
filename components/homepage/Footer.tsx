"use client";

import React from "react";
import { ArrowRight, BarChart2, Github } from "lucide-react";

interface FooterProps {
  onStartExploring: () => void;
  onNavigateSection: (sectionId: string) => void;
}

export default function Footer({ onStartExploring, onNavigateSection }: FooterProps) {
  return (
    <footer className="pt-12 pb-8 border-t border-slate-200/60 max-w-5xl mx-auto space-y-12">
      {/* Final CTA Banner */}
      <div className="bg-gradient-to-br from-slate-900 to-indigo-950 text-white rounded-3xl p-8 sm:p-10 text-center space-y-5 shadow-lg relative overflow-hidden">
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Ready to understand your data?
          </h2>
          <p className="text-xs sm:text-sm text-slate-300 max-w-md mx-auto">
            Upload your file or try a sample dataset. Powerful data exploration and reporting, completely free to use.
          </p>
        </div>

        <div className="pt-2">
          <button
            onClick={onStartExploring}
            className="inline-flex items-center gap-2 bg-white hover:bg-slate-100 text-slate-900 font-bold px-7 py-3 rounded-full text-xs shadow-md transition-all group"
          >
            <span>Start Exploring</span>
            <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>

      {/* Footer Navigation Columns */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-xs text-slate-600 px-2">
        {/* Brand Col */}
        <div className="space-y-3 md:col-span-1">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-slate-900 text-white flex items-center justify-center font-bold">
              <BarChart2 className="w-4 h-4 text-indigo-300" />
            </div>
            <span className="font-bold text-sm text-slate-900 tracking-tight">Analytix</span>
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            Powerful data exploration and reporting, free to use.
          </p>
          <a
            href="https://github.com/bhvyshrm/csv-explorer"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-slate-700 hover:text-slate-900 font-medium"
          >
            <Github className="w-3.5 h-3.5" />
            <span>GitHub Repository</span>
          </a>
        </div>

        {/* Navigation */}
        <div className="space-y-2">
          <h4 className="font-semibold text-slate-900 uppercase font-mono text-[10px] tracking-wider">
            Navigation
          </h4>
          <ul className="space-y-1.5">
            <li>
              <button
                onClick={() => onNavigateSection("hero")}
                className="hover:text-slate-900 transition-colors"
              >
                Home
              </button>
            </li>
            <li>
              <button
                onClick={() => onNavigateSection("quick-start")}
                className="hover:text-slate-900 transition-colors"
              >
                Explore Data
              </button>
            </li>
            <li>
              <button
                onClick={() => onNavigateSection("capabilities")}
                className="hover:text-slate-900 transition-colors"
              >
                Features
              </button>
            </li>
            <li>
              <button
                onClick={() => onNavigateSection("format-grid")}
                className="hover:text-slate-900 transition-colors"
              >
                Supported Formats
              </button>
            </li>
          </ul>
        </div>

        {/* Formats */}
        <div className="space-y-2">
          <h4 className="font-semibold text-slate-900 uppercase font-mono text-[10px] tracking-wider">
            Supported Formats
          </h4>
          <ul className="space-y-1.5 font-mono text-[11px] text-slate-500">
            <li>CSV (.csv)</li>
            <li>Excel (.xlsx, .xls)</li>
            <li>JSON (.json, .ndjson)</li>
            <li>Parquet (.parquet)</li>
            <li>TSV (.tsv, .tab)</li>
            <li>Logs & Text (.log, .txt)</li>
            <li>XML (.xml)</li>
          </ul>
        </div>

        {/* Legal & Trust */}
        <div className="space-y-2">
          <h4 className="font-semibold text-slate-900 uppercase font-mono text-[10px] tracking-wider">
            Privacy & Trust
          </h4>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            Data is analyzed in memory for the duration of the session and is never persisted to databases or shared with external third-party models.
          </p>
        </div>
      </div>

      {/* Copyright Line */}
      <div className="pt-6 border-t border-slate-200/40 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-400 font-mono gap-2">
        <span>© {new Date().getFullYear()} Analytix. All rights reserved.</span>
        <span>Explore data. Discover insights.</span>
      </div>
    </footer>
  );
}
