"use client";

import React, { useRef } from "react";
import {
  BarChart2,
  Home,
  Upload,
  Download,
  FileSpreadsheet,
  Layers,
  Menu,
  Sparkles,
} from "lucide-react";
import { AnalysisPayload } from "@/types/analytix";

interface WorkspaceTopBarProps {
  data: AnalysisPayload;
  onBackToHome: () => void;
  onReplaceFile: (file: File) => void;
  onSelectWorksheet: (sheetName: string) => void;
  onGoToReports: () => void;
  onToggleMobileSidebar: () => void;
  isLoadingSheet: boolean;
}

export default function WorkspaceTopBar({
  data,
  onBackToHome,
  onReplaceFile,
  onSelectWorksheet,
  onGoToReports,
  onToggleMobileSidebar,
  isLoadingSheet,
}: WorkspaceTopBarProps) {
  const replaceInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onReplaceFile(e.target.files[0]);
    }
  };

  const isExcel = Boolean(data.workbook_metadata && data.workbook_metadata.sheets.length > 0);

  return (
    <header className="h-16 border-b border-slate-200/80 bg-white/80 backdrop-blur-md sticky top-0 z-30 px-4 sm:px-6 flex items-center justify-between shadow-xs">
      {/* Hidden input for replace file */}
      <input
        ref={replaceInputRef}
        type="file"
        onChange={handleFileChange}
        className="hidden"
      />

      {/* Left: Hamburger (mobile), Analytix Logo, Home Link */}
      <div className="flex items-center gap-3">
        {/* Mobile menu toggle */}
        <button
          onClick={onToggleMobileSidebar}
          className="lg:hidden p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          aria-label="Toggle navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Brand & Home */}
        <div
          onClick={onBackToHome}
          className="flex items-center gap-2 cursor-pointer group select-none"
        >
          <div className="w-8 h-8 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold shadow-xs group-hover:bg-slate-800 transition-colors">
            <BarChart2 className="w-4 h-4 text-indigo-300" />
          </div>
          <span className="font-bold text-base text-slate-900 tracking-tight hidden sm:inline">
            Analytix
          </span>
        </div>

        <button
          onClick={onBackToHome}
          className="hidden sm:inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-900 bg-slate-100 hover:bg-slate-200/80 px-2.5 py-1 rounded-full transition-colors font-medium ml-1"
        >
          <Home className="w-3 h-3" />
          <span>Home</span>
        </button>
      </div>

      {/* Center: Current Dataset Name & Format Badge */}
      <div className="flex items-center gap-2 max-w-xs sm:max-w-md truncate">
        <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0"></span>
        <span className="text-xs sm:text-sm font-semibold text-slate-800 truncate font-mono">
          {data.dataset_name}
        </span>
        <span className="text-[10px] bg-slate-100 text-slate-700 border border-slate-200 font-mono px-2 py-0.5 rounded-full font-medium shrink-0">
          {data.dataset_format}
        </span>

        {/* Excel Worksheet Dropdown */}
        {isExcel && data.workbook_metadata && (
          <div className="hidden md:flex items-center gap-1.5 ml-2 pl-2 border-l border-slate-200">
            <Layers className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <select
              value={data.active_worksheet || ""}
              onChange={(e) => onSelectWorksheet(e.target.value)}
              disabled={isLoadingSheet}
              className="text-xs font-mono bg-slate-50 border border-slate-200 text-slate-800 rounded-lg px-2 py-1 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
            >
              {data.workbook_metadata.sheets.map((sheet) => (
                <option key={sheet.name} value={sheet.name}>
                  {sheet.name} ({sheet.row_count} rows)
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Right Actions: Replace File & Export Reports */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => replaceInputRef.current?.click()}
          className="flex items-center gap-1.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200/80 px-3 py-1.5 rounded-full text-xs font-medium shadow-xs transition-colors"
        >
          <Upload className="w-3.5 h-3.5 text-slate-500" />
          <span className="hidden sm:inline">Replace File</span>
        </button>

        <button
          onClick={onGoToReports}
          className="flex items-center gap-1.5 bg-slate-900 hover:bg-slate-800 text-white px-3.5 py-1.5 rounded-full text-xs font-semibold shadow-xs transition-colors"
        >
          <Download className="w-3.5 h-3.5 text-indigo-200" />
          <span>Reports</span>
        </button>
      </div>
    </header>
  );
}
