"use client";

import React, { useState, useEffect, useCallback } from "react";
import HomepageView from "@/components/homepage/HomepageView";
import WorkspaceTopBar from "@/components/workspace/WorkspaceTopBar";
import WorkspaceSidebar from "@/components/workspace/WorkspaceSidebar";
import OverviewView from "@/components/views/OverviewView";
import DataPreviewView from "@/components/views/DataPreviewView";
import DataQualityView from "@/components/views/DataQualityView";
import StatisticsView from "@/components/views/StatisticsView";
import VisualizationsView from "@/components/views/VisualizationsView";
import CorrelationsView from "@/components/views/CorrelationsView";
import OutlierAnalysisView from "@/components/views/OutlierAnalysisView";
import ReportCenterView from "@/components/views/ReportCenterView";
import { ActiveNavTab, AnalysisPayload, OutlierResult } from "@/types/analytix";
import { Loader2, AlertCircle, RefreshCw, ArrowLeft } from "lucide-react";

const MAX_UPLOAD_BYTES = 4.5 * 1024 * 1024; // 4.5 MB Vercel Serverless limit

/**
 * Safely extract meaningful error details from API responses.
 * Handles FastAPI string/structured details, plain text, and HTML error pages.
 */
async function extractErrorMessage(res: Response, fallbackMessage: string): Promise<string> {
  const statusInfo = res.status ? ` (${res.status} ${res.statusText || ""})`.trim() : "";
  try {
    const contentType = res.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      const data = await res.json();
      if (data) {
        if (typeof data.detail === "string" && data.detail.trim().length > 0) {
          return data.detail;
        }
        if (Array.isArray(data.detail) && data.detail.length > 0) {
          const msgs = data.detail
            .map((item: any) => {
              if (typeof item === "string") return item;
              if (item && typeof item === "object") {
                const loc = Array.isArray(item.loc) ? item.loc.slice(1).join(".") : "";
                return loc ? `${loc}: ${item.msg || "invalid value"}` : (item.msg || JSON.stringify(item));
              }
              return String(item);
            })
            .filter(Boolean);
          if (msgs.length > 0) return msgs.join("; ");
        }
        if (typeof data.detail === "object" && data.detail !== null) {
          return JSON.stringify(data.detail);
        }
        if (typeof data.message === "string" && data.message.trim().length > 0) {
          return data.message;
        }
        if (typeof data.error === "string" && data.error.trim().length > 0) {
          return data.error;
        }
      }
    } else {
      const text = await res.text();
      if (text && text.trim().length > 0) {
        if (text.includes("<html") || text.includes("<!DOCTYPE") || text.includes("<body")) {
          return `${fallbackMessage}${statusInfo}`;
        }
        if (text.length <= 300) {
          return text.trim();
        }
      }
    }
  } catch {
    // Parsing error fallback
  }
  return `${fallbackMessage}${statusInfo}`;
}

export default function Home() {
  const [viewMode, setViewMode] = useState<"landing" | "workspace">("landing");
  const [activeTab, setActiveTab] = useState<ActiveNavTab>("overview");
  const [data, setData] = useState<AnalysisPayload | null>(null);
  const [rawUploadedFile, setRawUploadedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isLoadingSheet, setIsLoadingSheet] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState<boolean>(false);

  // Load a sample dataset by endpoint URL
  const handleLoadSample = useCallback(
    async (endpoint: string = "/api/sample/csv") => {
      setIsLoading(true);
      setUploadError(null);
      try {
        const res = await fetch(endpoint);
        if (!res.ok) {
          const errorMsg = await extractErrorMessage(res, "Failed to load sample dataset.");
          throw new Error(errorMsg);
        }
        const payload: AnalysisPayload = await res.json();
        setData(payload);
        setRawUploadedFile(null);
        setActiveTab("overview");
        setViewMode("workspace");
      } catch (err: any) {
        setUploadError(err.message || "Failed to load sample dataset.");
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  // Universal File Upload (supports .csv, .xlsx, .xls, .tsv, .json, .ndjson, .parquet, .txt, .log, .xml)
  const handleFileUpload = async (file: File) => {
    setUploadError(null);

    // Enforce 4.5 MB Vercel Serverless Payload limit
    if (file.size > MAX_UPLOAD_BYTES) {
      const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
      setUploadError(
        `File exceeds Vercel's 4.5 MB serverless limit (${sizeMB} MB). Please choose a dataset under 4.5 MB.`
      );
      return;
    }

    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorMsg = await extractErrorMessage(res, `Failed to process file "${file.name}".`);
        throw new Error(errorMsg);
      }

      const payload: AnalysisPayload = await res.json();
      setData(payload);
      setRawUploadedFile(file);
      setActiveTab("overview");
      setViewMode("workspace");
    } catch (err: any) {
      setUploadError(err.message || "An unexpected error occurred during ingestion.");
    } finally {
      setIsLoading(false);
    }
  };

  // Switch active Excel worksheet
  const handleSelectWorksheet = async (sheetName: string) => {
    if (!data) return;
    setIsLoadingSheet(true);
    setUploadError(null);

    try {
      if (rawUploadedFile) {
        const formData = new FormData();
        formData.append("file", rawUploadedFile);
        formData.append("sheet_name", sheetName);

        const res = await fetch("/api/upload", {
          method: "POST",
          body: formData,
        });

        if (!res.ok) {
          const errorMsg = await extractErrorMessage(res, `Failed to load sheet "${sheetName}".`);
          throw new Error(errorMsg);
        }

        const payload: AnalysisPayload = await res.json();
        setData(payload);
      } else {
        // Built-in sample Excel
        const res = await fetch("/api/sample/excel");
        if (!res.ok) {
          const errorMsg = await extractErrorMessage(res, "Failed to reload sample sheet.");
          throw new Error(errorMsg);
        }
        const payload: AnalysisPayload = await res.json();
        setData(payload);
      }
    } catch (err: any) {
      setUploadError(err.message || "Failed to switch worksheet.");
    } finally {
      setIsLoadingSheet(false);
    }
  };

  // Recalculate outliers with custom multiplier
  const handleRecalculateOutliers = async (
    column: string,
    multiplier: number
  ): Promise<OutlierResult | null> => {
    if (!data || !data.preview || data.preview.length === 0) return null;

    try {
      const res = await fetch("/api/analysis/outliers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          data: data.preview,
          column,
          multiplier,
        }),
      });

      if (!res.ok) {
        const errorMsg = await extractErrorMessage(res, "Outlier recalculation failed.");
        throw new Error(errorMsg);
      }

      const outlierResult: OutlierResult = await res.json();
      return outlierResult;
    } catch {
      return null;
    }
  };

  // User triggers "Start Exploring" from Landing Page
  const handleStartExploring = () => {
    if (data) {
      setViewMode("workspace");
    } else {
      handleLoadSample("/api/sample/csv");
    }
  };

  return (
    <>
      {viewMode === "landing" ? (
        <HomepageView
          onStartExploring={handleStartExploring}
          onFileUpload={handleFileUpload}
          onLoadSample={handleLoadSample}
          isLoading={isLoading}
          uploadError={uploadError}
        />
      ) : (
        <div className="flex flex-col min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-indigo-500 selection:text-white">
          {/* Top Bar */}
          {data && (
            <WorkspaceTopBar
              data={data}
              onBackToHome={() => setViewMode("landing")}
              onReplaceFile={handleFileUpload}
              onSelectWorksheet={handleSelectWorksheet}
              onGoToReports={() => setActiveTab("reports")}
              onToggleMobileSidebar={() => setIsMobileSidebarOpen(!isMobileSidebarOpen)}
              isLoadingSheet={isLoadingSheet}
            />
          )}

          {/* Workspace Body: Sidebar + Main Content */}
          <div className="flex-1 flex min-w-0">
            {data && (
              <WorkspaceSidebar
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                data={data}
                isOpenMobile={isMobileSidebarOpen}
                onCloseMobile={() => setIsMobileSidebarOpen(false)}
              />
            )}

            <main className="flex-1 p-4 sm:p-6 md:p-8 max-w-7xl w-full mx-auto overflow-y-auto">
              {isLoading ? (
                <div className="flex flex-col items-center justify-center h-96 space-y-4">
                  <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
                  <p className="text-sm text-slate-500 font-mono">
                    Profiling dataset & computing descriptive diagnostics in memory...
                  </p>
                </div>
              ) : !data ? (
                <div className="flex flex-col items-center justify-center h-96 space-y-4 text-center">
                  <AlertCircle className="w-12 h-12 text-amber-500" />
                  <h2 className="text-lg font-bold text-slate-800">No Dataset Loaded</h2>
                  <p className="text-xs text-slate-500 max-w-sm">
                    Upload a file or load one of our sample datasets to start exploring.
                  </p>
                  <button
                    onClick={() => handleLoadSample("/api/sample/csv")}
                    className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 text-white px-5 py-2.5 rounded-full text-xs font-semibold shadow-sm transition-colors"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    Load Sample Superstore CSV
                  </button>
                </div>
              ) : (
                <>
                  {activeTab === "overview" && <OverviewView data={data} />}
                  {(activeTab === "data-preview" ||
                    activeTab === "data-explorer" ||
                    activeTab === "excel-explorer") && <DataPreviewView data={data} />}
                  {activeTab === "data-quality" && <DataQualityView data={data} />}
                  {activeTab === "statistics" && <StatisticsView data={data} />}
                  {activeTab === "visualizations" && <VisualizationsView data={data} />}
                  {activeTab === "correlations" && <CorrelationsView data={data} />}
                  {(activeTab === "outliers" || activeTab === "outlier-analysis") && (
                    <OutlierAnalysisView
                      data={data}
                      onRecalculateOutliers={handleRecalculateOutliers}
                    />
                  )}
                  {(activeTab === "reports" || activeTab === "export-reports") && (
                    <ReportCenterView data={data} />
                  )}
                </>
              )}
            </main>
          </div>
        </div>
      )}
    </>
  );
}
