"use client";

import React from "react";
import {
  Layers,
  Table,
  ShieldCheck,
  Calculator,
  BarChart3,
  GitFork,
  Target,
  Download,
  X,
  FileSpreadsheet,
} from "lucide-react";
import { ActiveNavTab, AnalysisPayload } from "@/types/analytix";

interface WorkspaceSidebarProps {
  activeTab: ActiveNavTab;
  setActiveTab: (tab: ActiveNavTab) => void;
  data: AnalysisPayload;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
}

interface NavItemDef {
  id: ActiveNavTab;
  label: string;
  icon: any;
  badge?: string;
  badgeColor?: string;
}

export default function WorkspaceSidebar({
  activeTab,
  setActiveTab,
  data,
  isOpenMobile,
  onCloseMobile,
}: WorkspaceSidebarProps) {
  const qualityScore = data.quality ? Math.round(data.quality.overall_health_score) : null;
  const outlierCount = data.outliers
    ? Object.values(data.outliers).reduce(
        (sum, o) => sum + (o ? o.flagged_count : 0),
        0
      )
    : 0;

  const navItems: NavItemDef[] = [
    {
      id: "overview",
      label: "Overview",
      icon: Layers,
    },
    {
      id: "data-preview",
      label: "Data Preview",
      icon: Table,
      badge: `${data.overview.total_rows.toLocaleString()} rows`,
      badgeColor: "bg-slate-100 text-slate-600 border-slate-200",
    },
    {
      id: "data-quality",
      label: "Data Quality",
      icon: ShieldCheck,
      badge: qualityScore !== null ? `${qualityScore}/100` : undefined,
      badgeColor:
        qualityScore !== null && qualityScore >= 85
          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
          : "bg-amber-50 text-amber-700 border-amber-200",
    },
    {
      id: "statistics",
      label: "Statistics",
      icon: Calculator,
      badge: `${data.overview.numeric_columns.length} cols`,
      badgeColor: "bg-slate-100 text-slate-600 border-slate-200",
    },
    {
      id: "visualizations",
      label: "Visualizations",
      icon: BarChart3,
    },
    {
      id: "correlations",
      label: "Correlations",
      icon: GitFork,
    },
    {
      id: "outliers",
      label: "Outliers",
      icon: Target,
      badge: outlierCount > 0 ? `${outlierCount} flagged` : "0 flagged",
      badgeColor:
        outlierCount > 0
          ? "bg-amber-50 text-amber-700 border-amber-200"
          : "bg-slate-100 text-slate-600 border-slate-200",
    },
    {
      id: "reports",
      label: "Report Center",
      icon: Download,
      badge: "Exports",
      badgeColor: "bg-indigo-50 text-indigo-700 border-indigo-200",
    },
  ];

  // Map legacy tabs to simplified tabs
  const normalizedActiveTab =
    activeTab === "data-explorer" || activeTab === "excel-explorer"
      ? "data-preview"
      : activeTab === "outlier-analysis"
      ? "outliers"
      : activeTab === "export-reports"
      ? "reports"
      : activeTab;

  const sidebarContent = (
    <div className="flex flex-col h-full justify-between p-4 bg-white/90 backdrop-blur-md border-r border-slate-200/80">
      <div>
        {/* Navigation Heading */}
        <div className="flex items-center justify-between px-3 mb-3">
          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">
            Analysis Workspace
          </span>
          <button
            onClick={onCloseMobile}
            className="lg:hidden p-1 text-slate-400 hover:text-slate-700 rounded-lg"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = normalizedActiveTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id);
                  onCloseMobile();
                }}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? "bg-slate-900 text-white font-semibold shadow-xs"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/80"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon
                    className={`w-4 h-4 ${
                      isActive ? "text-indigo-300" : "text-slate-400 group-hover:text-slate-600"
                    }`}
                  />
                  <span>{item.label}</span>
                </div>

                {item.badge && (
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded-full border font-medium ${
                      isActive ? "bg-white/20 text-white border-white/20" : item.badgeColor
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Dataset quick summary pill */}
      <div className="mt-6 p-3 bg-slate-50 border border-slate-200/70 rounded-2xl text-[11px] font-mono space-y-1 text-slate-600">
        <div className="flex justify-between">
          <span className="text-slate-400">Rows:</span>
          <span className="font-semibold text-slate-800">{data.overview.total_rows.toLocaleString()}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Columns:</span>
          <span className="font-semibold text-slate-800">{data.overview.total_columns}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Memory:</span>
          <span className="font-semibold text-slate-800">{data.overview.memory_usage_formatted}</span>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Persistent Sidebar */}
      <aside className="hidden lg:block w-64 h-[calc(100vh-4rem)] sticky top-16 z-20 shrink-0">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Overlay */}
      {isOpenMobile && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div
            onClick={onCloseMobile}
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs transition-opacity"
          />
          <div className="relative w-72 max-w-[80vw] h-full shadow-2xl z-10 animate-in slide-in-from-left duration-200">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
}
