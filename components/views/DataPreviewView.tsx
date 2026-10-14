"use client";

import React, { useState } from "react";
import { AnalysisPayload } from "@/types/analytix";
import { Table, Download } from "lucide-react";

interface DataPreviewViewProps {
  data: AnalysisPayload;
}

export default function DataPreviewView({ data }: DataPreviewViewProps) {
  const [rowLimit, setRowLimit] = useState(25);
  const rows = data.preview.slice(0, rowLimit);
  const columnNames = data.columns.map((c) => c["Column Name"]);

  const handleExportPreviewCSV = () => {
    if (rows.length === 0) return;
    const headers = columnNames.map((c) => `"${c}"`).join(",");
    const csvRows = rows.map((r) =>
      columnNames
        .map((col) => {
          const val = r[col];
          if (val === null || val === undefined) return "";
          return `"${String(val).replace(/"/g, '""')}"`;
        })
        .join(",")
    );
    const csvContent = [headers, ...csvRows].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${data.dataset_name}_preview.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-card border border-border rounded-xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-primary-text flex items-center gap-2">
              <Table className="w-5 h-5 text-accent" />
              Data Preview
            </h1>
            <p className="text-sm text-muted-text mt-0.5">
              Live in-memory inspection of the active dataset (first {data.preview.length} loaded records).
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-background border border-border rounded-lg px-3 py-1.5 text-xs">
              <span className="text-muted-text">Show:</span>
              {[10, 25, 50].map((limit) => (
                <button
                  key={limit}
                  onClick={() => setRowLimit(limit)}
                  className={`px-2 py-0.5 rounded font-mono text-xs transition-colors ${
                    rowLimit === limit
                      ? "bg-accent text-white font-semibold"
                      : "text-muted-text hover:text-primary-text"
                  }`}
                >
                  {limit}
                </button>
              ))}
            </div>

            <button
              onClick={handleExportPreviewCSV}
              className="flex items-center gap-2 bg-card-hover border border-border hover:border-accent text-primary-text px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
            >
              <Download className="w-3.5 h-3.5 text-accent" />
              Export Preview CSV
            </button>
          </div>
        </div>
      </div>

      {/* Tabular Preview */}
      <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto max-h-[620px]">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-background/95 sticky top-0 z-10 border-b border-border font-mono uppercase tracking-wider text-muted-text backdrop-blur-sm">
              <tr>
                <th className="py-2.5 px-3 border-r border-border/60 text-center w-12 bg-background/95">
                  #
                </th>
                {columnNames.map((colName) => (
                  <th
                    key={colName}
                    className="py-2.5 px-3 border-r border-border/40 whitespace-nowrap font-medium text-primary-text"
                  >
                    {colName}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 font-mono">
              {rows.length > 0 ? (
                rows.map((row, rIdx) => (
                  <tr
                    key={rIdx}
                    className="hover:bg-card-hover/80 transition-colors"
                  >
                    <td className="py-2 px-3 text-center text-muted-text/70 border-r border-border/60 bg-background/30 font-semibold select-none">
                      {rIdx + 1}
                    </td>
                    {columnNames.map((colName) => {
                      const val = row[colName];
                      const isNull = val === null || val === undefined;
                      return (
                        <td
                          key={colName}
                          className={`py-2 px-3 border-r border-border/40 whitespace-nowrap ${
                            isNull
                              ? "text-muted-text/50 italic bg-amber-950/10"
                              : "text-primary-text"
                          }`}
                        >
                          {isNull ? (
                            <span className="text-[10px] text-warning/80 bg-warning/10 px-1.5 py-0.5 rounded">
                              null
                            </span>
                          ) : typeof val === "boolean" ? (
                            <span
                              className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${
                                val
                                  ? "bg-teal-950/40 text-teal-300"
                                  : "bg-red-950/40 text-red-300"
                              }`}
                            >
                              {String(val)}
                            </span>
                          ) : (
                            String(val)
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan={columnNames.length + 1}
                    className="text-center py-10 text-sm text-muted-text"
                  >
                    No preview records available.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
