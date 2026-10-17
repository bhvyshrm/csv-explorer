"use client";

import React, { useState, useRef } from "react";
import {
  Upload,
  FileSpreadsheet,
  FileCode,
  FileText,
  Database,
  Sparkles,
  AlertCircle,
  Loader2,
  CheckCircle2,
  ArrowRight,
} from "lucide-react";

interface QuickStartUploadProps {
  onFileUpload: (file: File) => Promise<void>;
  onLoadSample: (endpoint: string) => Promise<void>;
  isLoading: boolean;
  uploadError: string | null;
}

const SUPPORTED_EXTENSIONS = [
  ".csv",
  ".xlsx",
  ".xls",
  ".tsv",
  ".json",
  ".ndjson",
  ".jsonl",
  ".parquet",
  ".txt",
  ".log",
  ".xml",
];

const SAMPLE_DATASETS = [
  {
    name: "Superstore Sales",
    format: "CSV",
    description: "122 rows of retail transactions with profits and sales",
    endpoint: "/api/sample/csv",
    badge: "Popular",
    icon: FileSpreadsheet,
  },
  {
    name: "Multisheet Retail",
    format: "Excel (.xlsx)",
    description: "3 sheets: Orders, Customer Demographics, Returns",
    endpoint: "/api/sample/excel",
    badge: "Multi-Sheet",
    icon: Database,
  },
  {
    name: "Tech Hardware",
    format: "JSON",
    description: "Nested hardware specs, prices, ratings, and stock",
    endpoint: "/api/sample/json",
    badge: "Nested",
    icon: FileCode,
  },
  {
    name: "Student Scores",
    format: "TSV",
    description: "Study hours, attendance rates, and exam performance",
    endpoint: "/api/sample/tsv",
    badge: "Tabular",
    icon: FileText,
  },
  {
    name: "Web Analytics",
    format: "Parquet",
    description: "Columnar web traffic sessions with revenue & devices",
    endpoint: "/api/sample/parquet",
    badge: "Columnar",
    icon: Sparkles,
  },
];

export default function QuickStartUpload({
  onFileUpload,
  onLoadSample,
  isLoading,
  uploadError,
}: QuickStartUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileUpload(e.target.files[0]);
    }
  };

  return (
    <section id="quick-start" className="py-8 max-w-4xl mx-auto space-y-6">
      {/* Title */}
      <div className="text-center space-y-1.5">
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
          Quick Start: Upload or Choose a Sample
        </h2>
        <p className="text-sm text-slate-600">
          Drop any supported file below or explore with one of our curated sample datasets.
        </p>
      </div>

      {/* Upload Dropzone Container */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-3xl p-8 sm:p-12 text-center cursor-pointer transition-all ${
          isDragging
            ? "border-indigo-500 bg-indigo-50/70 scale-[1.01]"
            : "border-slate-200/90 hover:border-slate-300 bg-white/70 hover:bg-white/90 backdrop-blur-md"
        } shadow-sm group`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={SUPPORTED_EXTENSIONS.join(",")}
          onChange={handleFileInputChange}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div
            className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-all ${
              isDragging
                ? "bg-indigo-600 text-white scale-110"
                : "bg-slate-100 group-hover:bg-indigo-50 text-slate-600 group-hover:text-indigo-600"
            }`}
          >
            {isLoading ? (
              <Loader2 className="w-7 h-7 animate-spin text-indigo-600" />
            ) : (
              <Upload className="w-7 h-7" />
            )}
          </div>

          <div className="space-y-1">
            <p className="text-base font-semibold text-slate-800">
              {isLoading
                ? "Profiling dataset and calculating descriptive statistics in memory..."
                : isDragging
                ? "Release to upload file"
                : "Drag & drop your file here, or click to browse"}
            </p>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              Supports CSV, Excel (.xlsx, .xls), JSON, Parquet, TSV, Text, Logs, and XML.
            </p>
          </div>

          <div className="inline-flex items-center gap-1.5 text-[11px] font-mono text-slate-600 bg-slate-100/90 px-3 py-1 rounded-full">
            <span>Serverless upload limit:</span>
            <strong className="text-slate-800">4.5 MB</strong>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {uploadError && (
        <div className="flex items-start gap-2.5 bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-2xl text-xs leading-relaxed animate-in fade-in">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold">Upload notice: </span>
            {uploadError}
          </div>
        </div>
      )}

      {/* Sample Datasets Row */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between text-xs text-slate-600 px-1">
          <span className="font-semibold uppercase tracking-wider text-[11px] text-slate-500 font-mono">
            Or try a sample dataset (1-click load)
          </span>
          <span className="text-[11px] text-slate-500">No upload required</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {SAMPLE_DATASETS.map((sample, idx) => {
            const Icon = sample.icon;
            return (
              <button
                key={idx}
                onClick={() => onLoadSample(sample.endpoint)}
                disabled={isLoading}
                className="bg-white/80 hover:bg-white border border-slate-200/80 hover:border-indigo-300 p-3.5 rounded-2xl text-left transition-all hover:shadow-sm group disabled:opacity-50"
              >
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-slate-100 text-slate-700 group-hover:bg-indigo-50 group-hover:text-indigo-600 transition-colors">
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <span className="text-xs font-semibold text-slate-800 group-hover:text-indigo-600 transition-colors">
                      {sample.name}
                    </span>
                  </div>
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-medium">
                    {sample.format}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 line-clamp-1 leading-normal">
                  {sample.description}
                </p>
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}
