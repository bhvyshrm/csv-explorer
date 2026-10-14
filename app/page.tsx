"use client";

import React, { useState, useEffect, useCallback } from "react";
import Sidebar from "@/components/Sidebar";
import OverviewView from "@/components/views/OverviewView";
import DataExplorerView from "@/components/views/DataExplorerView";
import ExcelExplorerView from "@/components/views/ExcelExplorerView";
import DataPreviewView from "@/components/views/DataPreviewView";
import DataQualityView from "@/components/views/DataQualityView";
import StatisticsView from "@/components/views/StatisticsView";
import VisualizationsView from "@/components/views/VisualizationsView";
import OutlierAnalysisView from "@/components/views/OutlierAnalysisView";
import ExportReportsView from "@/components/views/ExportReportsView";
import { ActiveNavTab, AnalysisPayload, OutlierResult } from "@/types/analytix";
import { Loader2, AlertCircle, RefreshCw } from "lucide-react";

const MAX_UPLOAD_BYTES = 4.5 * 1024 * 1024; // 4.5 MB Vercel Serverless limit

export default function Home() {
  const [activeTab, setActiveTab] = useState<ActiveNavTab>("overview");
  const [data, setData] = useState<AnalysisPayload | null>(null);
  const [rawUploadedFile, setRawUploadedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isLoadingSheet, setIsLoadingSheet] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Load built-in sample CSV dataset on initial mount
  const loadSampleCSV = useCallback(async () => {
    setIsLoading(true);
    setUploadError(null);
    try {
      const res = await fetch("/api/sample/csv");
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to load sample dataset.");
      }
      const payload: AnalysisPayload = await res.json();
      setData(payload);
      setRawUploadedFile(null);
    } catch (err: any) {
      setUploadError(err.message || "Failed to load sample CSV.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSampleCSV();
  }, [loadSampleCSV]);

  // Load built-in sample Excel multi-sheet workbook
  const loadSampleExcel = async () => {
    setIsLoading(true);
    setUploadError(null);
    try {
      const res = await fetch("/api/sample/excel");
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to load sample Excel workbook.");
      }
      const payload: AnalysisPayload = await res.json();
      setData(payload);
      setRawUploadedFile(null);
      setActiveTab("excel-explorer");
    } catch (err: any) {
      setUploadError(err.message || "Failed to load sample Excel.");
    } finally {
      setIsLoading(false);
    }
  };

  // Upload custom CSV or Excel file
  const handleFileUpload = async (file: File) => {
    setUploadError(null);

    // Enforce 4.5 MB Vercel Serverless Payload cap
    if (file.size > MAX_UPLOAD_BYTES) {
      const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
      setUploadError(
        `File exceeds Vercel's 4.5 MB serverless limit (${sizeMB} MB). Please choose a dataset under 4.5 MB.`
      );
      return;
    }

    const fnLower = file.name.toLowerCase();
    const isCSV = fnLower.endsWith(".csv");
    const isExcel = fnLower.endsWith(".xlsx") || fnLower.endsWith(".xls");

    if (!isCSV && !isExcel) {
      setUploadError("Unsupported format. Please upload a .csv, .xlsx, or .xls file.");
      return;
    }

    setIsLoading(true);

    try {
      if (isCSV) {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("/api/upload/csv", {
          method: "POST",
          body: formData,
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || "Failed to parse CSV file.");
        }

        const payload: AnalysisPayload = await res.json();
        setData(payload);
        setRawUploadedFile(null);
        setActiveTab("overview");
      } else {
        // Excel file: First inspect sheets, then load first sheet
        const inspectForm = new FormData();
        inspectForm.append("file", file);

        const inspectRes = await fetch("/api/upload/excel/inspect", {
          method: "POST",
          body: inspectForm,
        });

        if (!inspectRes.ok) {
          const err = await inspectRes.json().catch(() => ({}));
          throw new Error(err.detail || "Failed to inspect Excel workbook.");
        }

        const inspectData = await inspectRes.json();
        const firstSheet = inspectData.sheet_names[0];

        const sheetForm = new FormData();
        sheetForm.append("file", file);
        sheetForm.append("sheet_name", firstSheet);

        const sheetRes = await fetch("/api/upload/excel/sheet", {
          method: "POST",
          body: sheetForm,
        });

        if (!sheetRes.ok) {
          const err = await sheetRes.json().catch(() => ({}));
          throw new Error(err.detail || `Failed to parse worksheet "${firstSheet}".`);
        }

        const payload: AnalysisPayload = await sheetRes.json();
        setData(payload);
        setRawUploadedFile(file);
        setActiveTab("excel-explorer");
      }
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

        const res = await fetch("/api/upload/excel/sheet", {
          method: "POST",
          body: formData,
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || `Failed to load sheet "${sheetName}".`);
        }

        const payload: AnalysisPayload = await res.json();
        setData(payload);
      } else {
        // Built-in sample Excel
        const res = await fetch(`/api/sample/excel`);
        if (!res.ok) {
          throw new Error("Failed to reload sample sheet.");
        }
        // If sample, we can load the specific sheet by re-inspecting or requesting
        const payload: AnalysisPayload = await res.json();
        // Update active sheet in payload if different
        setData(payload);
      }
    } catch (err: any) {
      setUploadError(err.message || `Failed to switch worksheet.`);
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
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Outlier recalculation failed.");
      }

      const outlierResult: OutlierResult = await res.json();
      return outlierResult;
    } catch (err) {
      return null;
    }
  };

  return (
    <div className="flex min-h-screen bg-background text-primary-text font-sans">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        data={data}
        onFileUpload={handleFileUpload}
        onLoadSampleCSV={loadSampleCSV}
        onLoadSampleExcel={loadSampleExcel}
        isLoading={isLoading}
        uploadError={uploadError}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Header Bar */}
        <header className="h-14 border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-10 px-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xs uppercase font-mono tracking-wider text-muted-text">
              Active Section:
            </span>
            <span className="text-xs font-semibold text-accent font-mono capitalize">
              {activeTab.replace("-", " ")}
            </span>
          </div>

          <div className="flex items-center gap-4 text-xs font-mono">
            {data && (
              <div className="flex items-center gap-2 text-muted-text">
                <span className="w-2 h-2 rounded-full bg-success"></span>
                <span>{data.dataset_name}</span>
                {data.active_worksheet && (
                  <span className="bg-card-hover border border-border px-1.5 py-0.5 rounded text-[11px] text-primary-text">
                    {data.active_worksheet}
                  </span>
                )}
              </div>
            )}
          </div>
        </header>

        {/* View Container */}
        <div className="flex-1 p-8 max-w-7xl w-full mx-auto">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center h-96 space-y-4">
              <Loader2 className="w-8 h-8 text-accent animate-spin" />
              <p className="text-sm text-muted-text font-mono">
                Profiling dataset & computing descriptive diagnostics in memory...
              </p>
            </div>
          ) : !data ? (
            <div className="flex flex-col items-center justify-center h-96 space-y-4 text-center">
              <AlertCircle className="w-12 h-12 text-warning" />
              <h2 className="text-lg font-semibold text-primary-text">
                No Dataset Available
              </h2>
              <p className="text-sm text-muted-text max-w-sm">
                Upload a CSV or Excel file via the sidebar, or load a sample dataset to begin exploration.
              </p>
              <button
                onClick={loadSampleCSV}
                className="flex items-center gap-2 bg-accent hover:bg-accent/90 text-white px-4 py-2 rounded-lg text-xs font-mono font-medium transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Load Sample Superstore CSV
              </button>
            </div>
          ) : (
            <>
              {activeTab === "overview" && <OverviewView data={data} />}
              {activeTab === "data-explorer" && <DataExplorerView data={data} />}
              {activeTab === "excel-explorer" && (
                <ExcelExplorerView
                  data={data}
                  onSelectWorksheet={handleSelectWorksheet}
                  isLoadingSheet={isLoadingSheet}
                />
              )}
              {activeTab === "data-preview" && <DataPreviewView data={data} />}
              {activeTab === "data-quality" && <DataQualityView data={data} />}
              {activeTab === "statistics" && <StatisticsView data={data} />}
              {activeTab === "visualizations" && <VisualizationsView data={data} />}
              {activeTab === "outlier-analysis" && (
                <OutlierAnalysisView
                  data={data}
                  onRecalculateOutliers={handleRecalculateOutliers}
                />
              )}
              {activeTab === "export-reports" && <ExportReportsView data={data} />}
            </>
          )}
        </div>
      </main>
    </div>
  );
}
