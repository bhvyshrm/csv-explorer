"use client";

import React, { useRef } from "react";
import {
  FileSpreadsheet,
  FileCode,
  Layers,
  FileText,
  Database,
  ArrowRight,
  Sparkles,
  HardDrive,
  Clock,
  CheckCircle2,
} from "lucide-react";

interface FormatGridProps {
  onSelectFormatUpload: (formatId: string, acceptExtensions: string) => void;
  onSelectSample: (endpoint: string) => void;
}

interface FormatCardItem {
  id: string;
  name: string;
  category: string;
  description: string;
  extensions: string;
  isAvailable: boolean;
  statusBadge: "Available" | "Coming soon";
  bgColor: string;
  borderColor: string;
  iconBg: string;
  iconColor: string;
  icon: any;
  actionText: string;
  sampleEndpoint?: string;
}

export default function FormatGrid({ onSelectFormatUpload, onSelectSample }: FormatGridProps) {
  const cards: FormatCardItem[] = [
    {
      id: "csv",
      name: "CSV Explorer",
      category: "Tabular",
      description: "Delimited text parsing with automatic delimiter inference, UTF-8 BOM detection, and duplicate header disambiguation.",
      extensions: ".csv",
      isAvailable: true,
      statusBadge: "Available",
      bgColor: "bg-[#EEF7F2]/80 hover:bg-[#EEF7F2]",
      borderColor: "border-emerald-200/70",
      iconBg: "bg-emerald-100/80",
      iconColor: "text-emerald-700",
      icon: FileSpreadsheet,
      actionText: "Explore CSV",
      sampleEndpoint: "/api/sample/csv",
    },
    {
      id: "excel",
      name: "Excel Explorer",
      category: "Spreadsheet",
      description: "Multi-sheet workbook inspector with worksheet discovery, formula evaluation, date preservation, and sheet switching.",
      extensions: ".xlsx, .xls",
      isAvailable: true,
      statusBadge: "Available",
      bgColor: "bg-[#EFF6FF]/80 hover:bg-[#EFF6FF]",
      borderColor: "border-sky-200/70",
      iconBg: "bg-sky-100/80",
      iconColor: "text-sky-700",
      icon: Layers,
      actionText: "Inspect Workbook",
      sampleEndpoint: "/api/sample/excel",
    },
    {
      id: "json",
      name: "JSON Explorer",
      category: "Hierarchical",
      description: "Ingest standard JSON arrays and newline-delimited JSON (NDJSON/JSONL) with automated nested dot-notation flattening.",
      extensions: ".json, .ndjson, .jsonl",
      isAvailable: true,
      statusBadge: "Available",
      bgColor: "bg-[#F5F3FF]/80 hover:bg-[#F5F3FF]",
      borderColor: "border-purple-200/70",
      iconBg: "bg-purple-100/80",
      iconColor: "text-purple-700",
      icon: FileCode,
      actionText: "Parse JSON",
      sampleEndpoint: "/api/sample/json",
    },
    {
      id: "parquet",
      name: "Parquet Explorer",
      category: "Columnar",
      description: "Apache Parquet columnar reader powered by PyArrow, supporting schema introspection, dimensions, and typed analytics.",
      extensions: ".parquet",
      isAvailable: true,
      statusBadge: "Available",
      bgColor: "bg-[#FFF7ED]/80 hover:bg-[#FFF7ED]",
      borderColor: "border-amber-200/70",
      iconBg: "bg-amber-100/80",
      iconColor: "text-amber-700",
      icon: HardDrive,
      actionText: "Inspect Parquet",
      sampleEndpoint: "/api/sample/parquet",
    },
    {
      id: "text-log",
      name: "Text & Log Explorer",
      category: "Unstructured",
      description: "Parse application and web server access logs with timestamp extraction, severity classification, and line diagnostics.",
      extensions: ".txt, .log",
      isAvailable: true,
      statusBadge: "Available",
      bgColor: "bg-[#F0FDFA]/80 hover:bg-[#F0FDFA]",
      borderColor: "border-teal-200/70",
      iconBg: "bg-teal-100/80",
      iconColor: "text-teal-700",
      icon: FileText,
      actionText: "Analyze Logs",
      sampleEndpoint: "/api/sample/log",
    },
    {
      id: "database",
      name: "Database Explorer",
      category: "Relational",
      description: "Direct SQL database connectivity (PostgreSQL, MySQL, SQLite) for querying tables and executing schema profiling.",
      extensions: "SQL connection string",
      isAvailable: false,
      statusBadge: "Coming soon",
      bgColor: "bg-slate-100/70 hover:bg-slate-100/90",
      borderColor: "border-slate-200/80",
      iconBg: "bg-slate-200/70",
      iconColor: "text-slate-600",
      icon: Database,
      actionText: "Connect Database",
    },
  ];

  return (
    <section id="format-grid" className="py-12 max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
          Supported Format Explorers
        </h2>
        <p className="text-sm text-slate-600 max-w-xl mx-auto">
          Tailored parsing pipelines and validation rules for every data category. Only real, tested implementations are marked as Available.
        </p>
      </div>

      {/* Six Card Grid matching Reference Image */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.id}
              className={`rounded-3xl p-6 border ${card.borderColor} ${card.bgColor} backdrop-blur-md shadow-sm transition-all duration-300 flex flex-col justify-between group hover:-translate-y-1 hover:shadow-md`}
            >
              <div>
                {/* Top Row: Dual Badges and Status Indicator */}
                <div className="flex items-center justify-between mb-5">
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-9 h-9 rounded-xl ${card.iconBg} ${card.iconColor} flex items-center justify-center shadow-xs`}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] font-mono font-semibold uppercase tracking-wider bg-white/80 text-slate-700 px-2.5 py-1 rounded-full border border-white/90">
                      {card.category}
                    </span>
                  </div>

                  {/* Status Indicator */}
                  <span
                    className={`text-[10px] font-medium px-2.5 py-0.5 rounded-full border font-mono ${
                      card.isAvailable
                        ? "bg-emerald-50 text-emerald-700 border-emerald-200/80"
                        : "bg-slate-200/60 text-slate-600 border-slate-300/60"
                    }`}
                  >
                    {card.statusBadge}
                  </span>
                </div>

                {/* Card Title & Content */}
                <h3 className="text-lg font-bold text-slate-900 mb-2 tracking-tight">
                  {card.name}
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed mb-4">
                  {card.description}
                </p>
              </div>

              {/* Bottom Actions */}
              <div className="pt-3 border-t border-slate-200/40 space-y-2.5">
                <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                  <span>Formats:</span>
                  <span className="font-semibold text-slate-700">{card.extensions}</span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      if (card.isAvailable) {
                        onSelectFormatUpload(card.id, card.extensions);
                      }
                    }}
                    disabled={!card.isAvailable}
                    className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl text-xs font-semibold transition-all ${
                      card.isAvailable
                        ? "bg-slate-900 hover:bg-slate-800 text-white shadow-xs group-hover:shadow"
                        : "bg-slate-200 text-slate-400 cursor-not-allowed"
                    }`}
                  >
                    <span>{card.actionText}</span>
                    {card.isAvailable && (
                      <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                    )}
                  </button>

                  {card.sampleEndpoint && (
                    <button
                      onClick={() => onSelectSample(card.sampleEndpoint!)}
                      title="Load sample dataset"
                      className="p-2 bg-white/80 hover:bg-white text-slate-600 hover:text-slate-900 border border-slate-200/80 rounded-xl text-xs transition-colors"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
