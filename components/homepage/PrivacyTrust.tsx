"use client";

import React from "react";
import { ShieldCheck, Server, Lock, Clock, Database, CheckCircle2 } from "lucide-react";

export default function PrivacyTrust() {
  const points = [
    {
      title: "In-Memory Session Processing",
      description: "Uploaded files are loaded into transient serverless memory to compute statistical diagnostics, quality audits, and visualizations. No files are saved to permanent disk storage or databases.",
      icon: Server,
    },
    {
      title: "Zero Third-Party AI Data Sharing",
      description: "Your dataset is never transmitted to external AI APIs, language models, or advertising trackers. All diagnostics run natively on our Python pandas/numpy data engine.",
      icon: Lock,
    },
    {
      title: "Strict 4.5 MB Serverless Limit",
      description: "We enforce an honest 4.5 MB upload ceiling matching Vercel's serverless function payload limit, preventing browser freezes and serverless memory timeouts.",
      icon: Clock,
    },
    {
      title: "Supported File Formats",
      description: "Analytix natively supports CSV (.csv), Excel workbooks (.xlsx, .xls), JSON (.json, .ndjson, .jsonl), Parquet (.parquet), TSV (.tsv), Text (.txt), Logs (.log), and XML (.xml).",
      icon: Database,
    },
  ];

  return (
    <section id="privacy" className="py-12 max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-1.5 bg-emerald-50 border border-emerald-200/80 rounded-full px-3 py-1 text-[11px] font-mono text-emerald-800 font-medium">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>Honest & Transparent Architecture</span>
        </div>
        <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
          Privacy, Security & Processing Architecture
        </h2>
        <p className="text-sm text-slate-600 max-w-xl mx-auto">
          We believe in complete transparency about how your data is handled and where computations occur.
        </p>
      </div>

      {/* Grid of Trust Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {points.map((point, idx) => {
          const Icon = point.icon;
          return (
            <div
              key={idx}
              className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-2xl p-6 shadow-sm space-y-3"
            >
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-slate-100 text-slate-800">
                  <Icon className="w-5 h-5 text-indigo-600" />
                </div>
                <h3 className="text-sm font-bold text-slate-900">{point.title}</h3>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed font-normal">
                {point.description}
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
