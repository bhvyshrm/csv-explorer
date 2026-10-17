"use client";

import React, { useState } from "react";
import { AnalysisPayload } from "@/types/analytix";
import PlotlyChart from "@/components/PlotlyChart";
import {
  BarChart3,
  Sliders,
  Flame,
  PieChart,
  HelpCircle,
} from "lucide-react";

interface VisualizationsViewProps {
  data: AnalysisPayload;
}

export default function VisualizationsView({ data }: VisualizationsViewProps) {
  const { visualizations, overview } = data;
  const numCols = overview.numeric_columns;
  const catCols = overview.categorical_columns;

  const [selectedNumCol, setSelectedNumCol] = useState<string>(numCols[0] || "");
  const [selectedCatCol, setSelectedCatCol] = useState<string>(catCols[0] || "");
  const [activeChartType, setActiveChartType] = useState<
    "distribution" | "boxplot" | "categorical" | "correlation" | "missing"
  >("distribution");

  return (
    <div className="space-y-6">
      {/* Header & Chart Selector */}
      <div className="bg-card border border-border rounded-xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-indigo-600" />
              Interactive Visualizations
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Explore distributions, quartiles, category contributions, and correlation heatmaps.
            </p>
          </div>

          {/* Chart Type Navigation */}
          <div className="flex flex-wrap border border-border rounded-lg overflow-hidden p-1 bg-background text-xs font-medium">
            <button
              onClick={() => setActiveChartType("distribution")}
              className={`px-3 py-1.5 rounded transition-colors ${
                activeChartType === "distribution"
                  ? "bg-accent text-white font-semibold"
                  : "text-muted-text hover:text-primary-text"
              }`}
            >
              Distributions
            </button>
            <button
              onClick={() => setActiveChartType("boxplot")}
              className={`px-3 py-1.5 rounded transition-colors ${
                activeChartType === "boxplot"
                  ? "bg-accent text-white font-semibold"
                  : "text-muted-text hover:text-primary-text"
              }`}
            >
              Box Plots
            </button>
            <button
              onClick={() => setActiveChartType("categorical")}
              className={`px-3 py-1.5 rounded transition-colors ${
                activeChartType === "categorical"
                  ? "bg-accent text-white font-semibold"
                  : "text-muted-text hover:text-primary-text"
              }`}
            >
              Categorical Bars
            </button>
            <button
              onClick={() => setActiveChartType("correlation")}
              className={`px-3 py-1.5 rounded transition-colors ${
                activeChartType === "correlation"
                  ? "bg-accent text-white font-semibold"
                  : "text-muted-text hover:text-primary-text"
              }`}
            >
              Correlations
            </button>
            <button
              onClick={() => setActiveChartType("missing")}
              className={`px-3 py-1.5 rounded transition-colors ${
                activeChartType === "missing"
                  ? "bg-accent text-white font-semibold"
                  : "text-muted-text hover:text-primary-text"
              }`}
            >
              Missing Values
            </button>
          </div>
        </div>
      </div>

      {/* 1. Distribution Histograms */}
      {activeChartType === "distribution" && (
        <div className="space-y-4">
          {numCols.length > 0 ? (
            <div className="bg-card border border-border rounded-xl p-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <div>
                  <h3 className="font-semibold text-primary-text text-base">
                    Numeric Frequency Distribution: {selectedNumCol}
                  </h3>
                  <p className="text-xs text-muted-text">
                    Dynamic histogram rendered with dashed Mean and Median indicators.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-text font-mono">Column:</span>
                  <select
                    value={selectedNumCol}
                    onChange={(e) => setSelectedNumCol(e.target.value)}
                    className="bg-background border border-border focus:border-accent text-primary-text text-xs rounded px-3 py-1.5 outline-none font-mono cursor-pointer"
                  >
                    {numCols.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <PlotlyChart
                figure={visualizations.histograms[selectedNumCol]}
                height={400}
              />
            </div>
          ) : (
            <div className="bg-card border border-border rounded-xl p-8 text-center text-sm text-muted-text">
              No numeric columns available to render distribution histograms.
            </div>
          )}
        </div>
      )}

      {/* 2. Box Plots */}
      {activeChartType === "boxplot" && (
        <div className="space-y-4">
          {numCols.length > 0 ? (
            <div className="bg-card border border-border rounded-xl p-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <div>
                  <h3 className="font-semibold text-primary-text text-base">
                    Spread & Quartiles: {selectedNumCol}
                  </h3>
                  <p className="text-xs text-muted-text">
                    Five-number summary box plot depicting Q1, Median, Q3, and individual outlier points.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-text font-mono">Column:</span>
                  <select
                    value={selectedNumCol}
                    onChange={(e) => setSelectedNumCol(e.target.value)}
                    className="bg-background border border-border focus:border-accent text-primary-text text-xs rounded px-3 py-1.5 outline-none font-mono cursor-pointer"
                  >
                    {numCols.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <PlotlyChart
                figure={visualizations.box_plots[selectedNumCol]}
                height={400}
              />
            </div>
          ) : (
            <div className="bg-card border border-border rounded-xl p-8 text-center text-sm text-muted-text">
              No numeric columns available to render box plots.
            </div>
          )}
        </div>
      )}

      {/* 3. Categorical Bars */}
      {activeChartType === "categorical" && (
        <div className="space-y-4">
          {catCols.length > 0 ? (
            <div className="bg-card border border-border rounded-xl p-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <div>
                  <h3 className="font-semibold text-primary-text text-base">
                    Categorical Breakdown: {selectedCatCol}
                  </h3>
                  <p className="text-xs text-muted-text">
                    Sorted frequency bar chart with percentage contribution annotations.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-text font-mono">Column:</span>
                  <select
                    value={selectedCatCol}
                    onChange={(e) => setSelectedCatCol(e.target.value)}
                    className="bg-background border border-border focus:border-accent text-primary-text text-xs rounded px-3 py-1.5 outline-none font-mono cursor-pointer"
                  >
                    {catCols.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <PlotlyChart
                figure={visualizations.category_bars[selectedCatCol]}
                height={400}
              />
            </div>
          ) : (
            <div className="bg-card border border-border rounded-xl p-8 text-center text-sm text-muted-text">
              No categorical columns available for bar chart visualization.
            </div>
          )}
        </div>
      )}

      {/* 4. Correlation Heatmap */}
      {activeChartType === "correlation" && (
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="mb-4">
            <h3 className="font-semibold text-primary-text text-base flex items-center gap-2">
              <Flame className="w-4 h-4 text-accent" />
              Pearson Linear Correlation Heatmap
            </h3>
            <p className="text-xs text-muted-text">
              Diverging color gradient (-1.0 to +1.0) displaying pairwise correlation across numeric variables.
            </p>
          </div>
          {visualizations.correlation_heatmap ? (
            <PlotlyChart
              figure={visualizations.correlation_heatmap}
              height={460}
            />
          ) : (
            <div className="p-8 text-center text-sm text-muted-text">
              At least two numeric columns with non-zero variance are required to compute correlations.
            </div>
          )}
        </div>
      )}

      {/* 5. Missing Values Bar Chart */}
      {activeChartType === "missing" && (
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="mb-4">
            <h3 className="font-semibold text-primary-text text-base">
              Missing Values Density Across Columns
            </h3>
            <p className="text-xs text-muted-text">
              Horizontal breakdown showing missing record counts and proportions per feature.
            </p>
          </div>
          {visualizations.missing_values ? (
            <PlotlyChart
              figure={visualizations.missing_values}
              height={400}
            />
          ) : (
            <div className="p-8 text-center text-sm text-muted-text">
              No missing value chart data available.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
