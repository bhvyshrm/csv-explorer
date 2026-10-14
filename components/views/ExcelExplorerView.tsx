"use client";

import React, { useState } from "react";
import { AnalysisPayload, SheetMetadata } from "@/types/analytix";
import { FileSpreadsheet, CheckCircle2, AlertCircle, ArrowRight, Loader2 } from "lucide-react";

interface ExcelExplorerViewProps {
  data: AnalysisPayload;
  onSelectWorksheet: (sheetName: string) => Promise<void>;
  isLoadingSheet: boolean;
}

export default function ExcelExplorerView({
  data,
  onSelectWorksheet,
  isLoadingSheet,
}: ExcelExplorerViewProps) {
  const meta = data.workbook_metadata;
  const [selectedSheet, setSelectedSheet] = useState<string>(
    data.active_worksheet || (meta?.sheet_names[0] ?? "")
  );

  if (!meta) {
    return (
      <div className="bg-card border border-border rounded-xl p-8 text-center">
        <FileSpreadsheet className="w-12 h-12 text-muted-text mx-auto mb-3" />
        <h2 className="text-lg font-semibold text-primary-text">
          No Excel Workbook Loaded
        </h2>
        <p className="text-sm text-muted-text max-w-md mx-auto mt-1">
          The current active dataset ({data.dataset_name}) is a {data.dataset_format} file.
          Upload a multi-sheet Excel (.xlsx or .xls) file or load the sample Excel workbook from the sidebar to use the Excel Explorer.
        </p>
      </div>
    );
  }

  const handleSheetChange = async (sheetName: string) => {
    setSelectedSheet(sheetName);
    await onSelectWorksheet(sheetName);
  };

  return (
    <div className="space-y-6">
      {/* Header Overview Card */}
      <div className="bg-card border border-border rounded-xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs uppercase tracking-wider font-semibold text-accent-secondary bg-accent-secondary/10 px-2 py-0.5 rounded">
                Workbook Overview
              </span>
              <span className="text-xs text-muted-text font-mono">
                {meta.file_format} • {meta.total_sheets} Worksheets
              </span>
            </div>
            <h1 className="text-xl font-bold text-primary-text">
              {data.dataset_name}
            </h1>
            <p className="text-sm text-muted-text mt-0.5">
              Inspect multi-sheet workbook structure, estimated boundaries, and switch active sheets.
            </p>
          </div>

          {/* Quick Active Sheet Switcher Dropdown */}
          <div className="flex items-center gap-3 bg-background border border-border p-2 rounded-lg">
            <span className="text-xs text-muted-text whitespace-nowrap pl-1">
              Active Sheet:
            </span>
            <select
              value={data.active_worksheet || ""}
              onChange={(e) => handleSheetChange(e.target.value)}
              disabled={isLoadingSheet}
              className="bg-card border border-border focus:border-accent text-primary-text text-sm rounded px-3 py-1.5 outline-none font-mono cursor-pointer disabled:opacity-50"
            >
              {meta.sheet_names.map((name) => (
                <option key={name} value={name}>
                  {name} {name === data.active_worksheet ? "✓ (Active)" : ""}
                </option>
              ))}
            </select>
            {isLoadingSheet && <Loader2 className="w-4 h-4 text-accent animate-spin" />}
          </div>
        </div>
      </div>

      {/* Sheets Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {meta.sheets.map((sheet: SheetMetadata, idx: number) => {
          const isActive = sheet.name === data.active_worksheet;
          return (
            <div
              key={idx}
              className={`bg-card border rounded-xl p-5 flex flex-col justify-between transition-all ${
                isActive
                  ? "border-accent ring-1 ring-accent/30 shadow-md"
                  : "border-border hover:border-border/80"
              }`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <h3 className="font-semibold text-primary-text text-base font-mono truncate flex items-center gap-1.5">
                    <FileSpreadsheet
                      className={`w-4 h-4 ${isActive ? "text-accent" : "text-muted-text"}`}
                    />
                    {sheet.name}
                  </h3>
                  {isActive ? (
                    <span className="flex items-center gap-1 text-xs text-accent font-medium bg-accent/10 px-2 py-0.5 rounded">
                      <CheckCircle2 className="w-3 h-3" />
                      Active
                    </span>
                  ) : sheet.is_empty ? (
                    <span className="flex items-center gap-1 text-xs text-warning bg-warning/10 px-2 py-0.5 rounded font-medium">
                      <AlertCircle className="w-3 h-3" />
                      Empty Sheet
                    </span>
                  ) : null}
                </div>

                {/* Dimensions */}
                <div className="grid grid-cols-2 gap-2 my-3 text-xs font-mono">
                  <div className="bg-background/60 p-2 rounded border border-border/60">
                    <span className="text-muted-text block text-[10px] uppercase">
                      Est. Rows
                    </span>
                    <span className="font-semibold text-primary-text text-sm">
                      {sheet.row_count.toLocaleString()}
                    </span>
                  </div>
                  <div className="bg-background/60 p-2 rounded border border-border/60">
                    <span className="text-muted-text block text-[10px] uppercase">
                      Est. Columns
                    </span>
                    <span className="font-semibold text-primary-text text-sm">
                      {sheet.col_count.toLocaleString()}
                    </span>
                  </div>
                </div>

                {/* Sample Headers */}
                <div className="mt-3">
                  <span className="text-[11px] uppercase tracking-wider text-muted-text font-medium block mb-1.5">
                    Sample Column Headers
                  </span>
                  <div className="flex flex-wrap gap-1 max-h-24 overflow-y-auto">
                    {sheet.sample_headers.length > 0 ? (
                      sheet.sample_headers.map((h, hIdx) => (
                        <span
                          key={hIdx}
                          className="text-[11px] bg-background border border-border/80 text-muted-text px-1.5 py-0.5 rounded font-mono truncate max-w-[140px]"
                        >
                          {h}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-muted-text italic">
                        No headers found in first row
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <div className="mt-5 pt-3 border-t border-border/60">
                {isActive ? (
                  <div className="text-center text-xs text-accent font-medium py-1.5 bg-accent/5 rounded border border-accent/20">
                    Currently Selected & Analyzed
                  </div>
                ) : (
                  <button
                    onClick={() => handleSheetChange(sheet.name)}
                    disabled={isLoadingSheet}
                    className="w-full flex items-center justify-center gap-1.5 bg-card-hover border border-border hover:border-accent hover:text-accent text-primary-text py-2 rounded-lg text-xs font-medium transition-all disabled:opacity-50"
                  >
                    <span>Analyze This Sheet</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
