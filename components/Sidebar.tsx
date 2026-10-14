"use client";

import React, { useRef } from "react";
import { ActiveNavTab, AnalysisPayload } from "@/types/analytix";
import {
  Layers,
  Columns,
  FileSpreadsheet,
  Table,
  ShieldCheck,
  Calculator,
  BarChart3,
  Target,
  Download,
  Upload,
  Database,
  Sparkles,
  Loader2,
  AlertCircle,
} from "lucide-react";

interface SidebarProps {
  activeTab: ActiveNavTab;
  setActiveTab: (tab: ActiveNavTab) => void;
  data: AnalysisPayload | null;
  onFileUpload: (file: File) => Promise<void>;
  onLoadSampleCSV: () => Promise<void>;
  onLoadSampleExcel: () => Promise<void>;
  isLoading: boolean;
  uploadError: string | null;
}

interface NavItem {
  id: ActiveNavTab;
  label: string;
  icon: any;
  badge?: string;
  badgeColor?: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

export default function Sidebar({
  activeTab,
  setActiveTab,
  data,
  onFileUpload,
  onLoadSampleCSV,
  onLoadSampleExcel,
  isLoading,
  uploadError,
}: SidebarProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileUpload(e.target.files[0]);
    }
  };

  const navSections: NavSection[] = [
    {
      title: "WORKSPACE",
      items: [
        { id: "overview" as ActiveNavTab, label: "Overview", icon: Layers },
      ],
    },
    {
      title: "EXPLORE",
      items: [
        { id: "data-explorer" as ActiveNavTab, label: "Data Explorer", icon: Columns },
        {
          id: "excel-explorer" as ActiveNavTab,
          label: "Excel Explorer",
          icon: FileSpreadsheet,
          badge: data?.workbook_metadata
            ? `${data.workbook_metadata.total_sheets} Sheets`
            : undefined,
        },
        { id: "data-preview" as ActiveNavTab, label: "Data Preview", icon: Table },
      ],
    },
    {
      title: "ANALYZE",
      items: [
        {
          id: "data-quality" as ActiveNavTab,
          label: "Data Quality",
          icon: ShieldCheck,
          badge: data?.quality
            ? `${data.quality.overall_health_score.toFixed(0)}`
            : undefined,
          badgeColor:
            data?.quality && data.quality.overall_health_score >= 85
              ? "text-success bg-success/10 border-success/30"
              : "text-warning bg-warning/10 border-warning/30",
        },
        { id: "statistics" as ActiveNavTab, label: "Statistics", icon: Calculator },
        { id: "visualizations" as ActiveNavTab, label: "Visualizations", icon: BarChart3 },
        { id: "outlier-analysis" as ActiveNavTab, label: "Outlier Analysis", icon: Target },
      ],
    },
    {
      title: "EXPORT",
      items: [
        { id: "export-reports" as ActiveNavTab, label: "Export Reports", icon: Download },
      ],
    },
  ];

  return (
    <aside className="w-72 bg-card border-r border-border flex flex-col h-screen sticky top-0 select-none z-20">
      {/* Brand Header */}
      <div className="p-5 border-b border-border">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-purple-600 flex items-center justify-center text-white font-bold text-lg shadow-md shadow-accent/20">
            ◈
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold tracking-tight text-primary-text text-base">
                Analytix
              </span>
              <span className="text-[10px] bg-accent/20 text-accent font-mono px-1.5 py-0.2 rounded font-semibold">
                2.0
              </span>
            </div>
            <p className="text-[11px] text-muted-text">
              Explore data. Discover insights.
            </p>
          </div>
        </div>
      </div>

      {/* Dataset & Ingestion Controls */}
      <div className="p-4 border-b border-border space-y-3">
        {/* Upload Button Box */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileChange}
          className="hidden"
        />

        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading}
          className="w-full flex items-center justify-center gap-2 bg-background border border-border border-dashed hover:border-accent text-primary-text py-2.5 px-3 rounded-lg text-xs font-medium transition-all group disabled:opacity-50"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 text-accent animate-spin" />
          ) : (
            <Upload className="w-4 h-4 text-accent group-hover:scale-110 transition-transform" />
          )}
          <span>Upload CSV or Excel</span>
        </button>
        <p className="text-[10px] text-muted-text text-center font-mono">
          Supports .csv, .xlsx, .xls (max 4.5 MB)
        </p>

        {uploadError && (
          <div className="flex items-start gap-1.5 bg-danger/10 border border-danger/30 text-danger p-2 rounded text-[11px] leading-tight">
            <AlertCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
            <span>{uploadError}</span>
          </div>
        )}

        {/* Quick Sample Buttons */}
        <div className="grid grid-cols-2 gap-2 pt-1">
          <button
            onClick={onLoadSampleCSV}
            disabled={isLoading}
            className="flex items-center justify-center gap-1 bg-card-hover border border-border/80 hover:border-accent/60 text-muted-text hover:text-primary-text py-1.5 px-2 rounded text-[11px] font-mono transition-colors disabled:opacity-50"
          >
            <Sparkles className="w-3 h-3 text-accent" />
            <span>Sample CSV</span>
          </button>

          <button
            onClick={onLoadSampleExcel}
            disabled={isLoading}
            className="flex items-center justify-center gap-1 bg-card-hover border border-border/80 hover:border-accent-secondary/60 text-muted-text hover:text-primary-text py-1.5 px-2 rounded text-[11px] font-mono transition-colors disabled:opacity-50"
          >
            <Database className="w-3 h-3 text-accent-secondary" />
            <span>Sample Excel</span>
          </button>
        </div>
      </div>

      {/* Navigation Sections */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-5">
        {navSections.map((sec, sIdx) => (
          <div key={sIdx}>
            <div className="px-3 mb-1.5 text-[10px] font-semibold text-muted-text/80 tracking-wider font-mono">
              {sec.title}
            </div>
            <div className="space-y-0.5">
              {sec.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? "bg-accent/15 text-accent font-semibold border-l-2 border-accent"
                        : "text-muted-text hover:text-primary-text hover:bg-card-hover"
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon
                        className={`w-4 h-4 ${
                          isActive ? "text-accent" : "text-muted-text"
                        }`}
                      />
                      <span>{item.label}</span>
                    </div>

                    {item.badge && (
                      <span
                        className={`text-[10px] font-mono px-1.5 py-0.2 rounded border ${
                          item.badgeColor ||
                          "text-accent-secondary bg-accent-secondary/10 border-accent-secondary/30"
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Footer Info */}
      <div className="p-3 border-t border-border text-[11px] text-muted-text/70 flex items-center justify-between font-mono">
        <span>Analytix v2.0.0</span>
        <span className="text-success flex items-center gap-1 text-[10px]">
          <span className="w-1.5 h-1.5 rounded-full bg-success"></span>
          Connected
        </span>
      </div>
    </aside>
  );
}
