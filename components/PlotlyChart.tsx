"use client";

import React, { useEffect, useRef } from "react";
import { PlotlyFigureSpec } from "@/types/analytix";

interface PlotlyChartProps {
  figure?: PlotlyFigureSpec | null;
  className?: string;
  height?: number;
}

export default function PlotlyChart({ figure, className = "", height = 380 }: PlotlyChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let isMounted = true;
    if (!containerRef.current || !figure || !figure.data) return;

    import("plotly.js-dist-min").then((PlotlyModule) => {
      const Plotly = PlotlyModule.default || PlotlyModule;
      if (!isMounted || !containerRef.current) return;

      const darkLayout = {
        ...figure.layout,
        autosize: true,
        height: height,
        paper_bgcolor: "#151824",
        plot_bgcolor: "#151824",
        font: {
          family: "Inter, sans-serif",
          color: "#F5F6FA",
          size: 12,
          ...(figure.layout?.font || {}),
        },
        margin: { t: 40, r: 25, l: 50, b: 50, ...(figure.layout?.margin || {}) },
      };

      Plotly.newPlot(containerRef.current, figure.data, darkLayout, {
        responsive: true,
        displayModeBar: false,
      });
    });

    return () => {
      isMounted = false;
      if (containerRef.current) {
        import("plotly.js-dist-min").then((PlotlyModule) => {
          const Plotly = PlotlyModule.default || PlotlyModule;
          if (containerRef.current) {
            try {
              Plotly.purge(containerRef.current);
            } catch {
              // Ignore cleanup purge errors
            }
          }
        });
      }
    };
  }, [figure, height]);

  if (!figure || !figure.data || figure.data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center bg-card rounded-lg border border-border text-muted-text text-sm p-8 ${className}`}
        style={{ height }}
      >
        No visualization data available for this selection.
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`w-full rounded-lg overflow-hidden bg-card border border-border ${className}`}
      style={{ minHeight: height }}
    />
  );
}
