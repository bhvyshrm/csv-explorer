"use client";

import React, { useState } from "react";
import { AnalysisPayload, PlotlyFigureSpec } from "@/types/analytix";
import PlotlyChart from "@/components/PlotlyChart";
import { GitFork, Info, RefreshCw, AlertCircle, Download } from "lucide-react";

interface CorrelationsViewProps {
  data: AnalysisPayload;
}

export default function CorrelationsView({ data }: CorrelationsViewProps) {
  const numericCols = data.overview.numeric_columns;
  const [selectedCols, setSelectedCols] = useState<string[]>(
    numericCols.slice(0, Math.min(8, numericCols.length))
  );
  const [method, setMethod] = useState<string>("pearson");
  const [chartFigure, setChartFigure] = useState<PlotlyFigureSpec | null>(
    data.visualizations.correlation_heatmap || null
  );
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleToggleCol = (col: string) => {
    if (selectedCols.includes(col)) {
      if (selectedCols.length <= 2) {
        setErrorMsg("Correlation requires at least 2 numeric columns.");
        return;
      }
      setSelectedCols(selectedCols.filter((c) => c !== col));
    } else {
      setSelectedCols([...selectedCols, col]);
    }
    setErrorMsg(null);
  };

  const handleRecalculate = async () => {
    if (selectedCols.length < 2) {
      setErrorMsg("Please select at least 2 columns to calculate correlations.");
      return;
    }
    setIsLoading(true);
    setErrorMsg(null);

    try {
      const res = await fetch("/api/analysis/correlation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          data: data.preview,
          columns: selectedCols,
          method: method,
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to recalculate correlation matrix.");
      }

      const fig = await res.json();
      setChartFigure(fig);
    } catch (err: any) {
      setErrorMsg(err.message || "Error computing correlation matrix.");
    } finally {
      setIsLoading(false);
    }
  };

  if (numericCols.length < 2) {
    return (
      <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-3xl p-8 text-center space-y-3">
        <AlertCircle className="w-10 h-10 text-amber-500 mx-auto" />
        <h3 className="text-base font-bold text-slate-800">Insufficient Numeric Columns</h3>
        <p className="text-xs text-slate-600 max-w-md mx-auto">
          Correlation analysis requires at least two numeric columns. This dataset contains {numericCols.length} numeric column(s).
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-3xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <GitFork className="w-5 h-5 text-indigo-600" />
              Correlation Analysis
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Analyze linear and monotonic pairwise relationships across numeric columns in {data.dataset_name}.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={method}
              onChange={(e) => setMethod(e.target.value)}
              className="text-xs font-mono bg-slate-50 border border-slate-200 text-slate-800 rounded-xl px-3 py-2 focus:ring-1 focus:ring-indigo-500 cursor-pointer"
            >
              <option value="pearson">Pearson (Linear)</option>
              <option value="spearman">Spearman (Rank/Monotonic)</option>
              <option value="kendall">Kendall (Concordance)</option>
            </select>

            <button
              onClick={handleRecalculate}
              disabled={isLoading}
              className="flex items-center gap-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs px-4 py-2 rounded-xl font-medium transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
              <span>Update Matrix</span>
            </button>
          </div>
        </div>

        {errorMsg && (
          <div className="mt-3 text-xs text-rose-700 bg-rose-50 border border-rose-200 p-2.5 rounded-xl">
            {errorMsg}
          </div>
        )}
      </div>

      {/* Column Selector Pills */}
      <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-3xl p-5 shadow-sm space-y-3">
        <div className="flex items-center justify-between text-xs text-slate-600">
          <span className="font-semibold uppercase tracking-wider font-mono text-[10px] text-slate-400">
            Selected Columns ({selectedCols.length} of {numericCols.length})
          </span>
          <span className="text-[11px] text-slate-500">Click to toggle column inclusion</span>
        </div>

        <div className="flex flex-wrap gap-2">
          {numericCols.map((col) => {
            const isSelected = selectedCols.includes(col);
            return (
              <button
                key={col}
                onClick={() => handleToggleCol(col)}
                className={`text-xs font-mono px-3 py-1.5 rounded-xl border transition-all ${
                  isSelected
                    ? "bg-indigo-50 border-indigo-200 text-indigo-700 font-semibold shadow-xs"
                    : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                }`}
              >
                {col}
              </button>
            );
          })}
        </div>
      </div>

      {/* Heatmap Container */}
      <div className="bg-white/85 backdrop-blur-md border border-slate-200/80 rounded-3xl p-6 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider font-mono">
          Correlation Heatmap ({method.toUpperCase()})
        </h3>
        <PlotlyChart figure={chartFigure} height={460} theme="light" />
      </div>

      {/* Educational Guide */}
      <div className="bg-slate-50/80 border border-slate-200/70 rounded-2xl p-4 text-xs text-slate-600 space-y-1.5">
        <div className="flex items-center gap-2 font-bold text-slate-800">
          <Info className="w-4 h-4 text-indigo-600" />
          <span>Interpreting Correlation Coefficients</span>
        </div>
        <p className="leading-relaxed">
          Values range from <strong>-1.0</strong> (perfect negative relationship) to <strong>+1.0</strong> (perfect positive relationship). Coefficients around <strong>0.0</strong> indicate no linear association. Note that correlation does not imply causation.
        </p>
      </div>
    </div>
  );
}
