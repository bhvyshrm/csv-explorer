"use client";

import React, { useState, useMemo } from "react";
import { AnalysisPayload } from "@/types/analytix";
import { Table, Download, Search, FileText } from "lucide-react";

interface DataPreviewViewProps {
  data: AnalysisPayload;
}

export default function DataPreviewView({ data }: DataPreviewViewProps) {
  const [rowLimit, setRowLimit] = useState(25);
  const [searchTerm, setSearchTerm] = useState("");

  const columnMetaMap = useMemo(() => {
    const map: Record<string, string> = {};
    data.columns.forEach((col) => {
      map[col["Column Name"]] = col["Inferred Type"] || col["Python dtype"];
    });
    return map;
  }, [data.columns]);

  const columnNames = useMemo(
    () => data.columns.map((c) => c["Column Name"]),
    [data.columns]
  );

  const filteredRows = useMemo(() => {
    if (!searchTerm.trim()) {
      return data.preview.slice(0, rowLimit);
    }
    const lower = searchTerm.toLowerCase();
    return data.preview
      .filter((row) =>
        Object.values(row).some((val) =>
          val !== null && val !== undefined && String(val).toLowerCase().includes(lower)
        )
      )
      .slice(0, rowLimit);
  }, [data.preview, searchTerm, rowLimit]);

  const handleExportPreviewCSV = () => {
    if (filteredRows.length === 0) return;
    const headers = columnNames.map((c) => `"${c}"`).join(",");
    const csvRows = filteredRows.map((r) =>
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
      <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-3xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <Table className="w-5 h-5 text-indigo-600" />
              Data Preview
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Live in-memory inspection of active dataset (showing {filteredRows.length} of {data.preview.length} loaded records, out of {data.overview.total_rows.toLocaleString()} total rows).
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Search filter input */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search preview..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:ring-1 focus:ring-indigo-500 focus:outline-none w-44 font-mono text-slate-800"
              />
            </div>

            {/* Row limit picker */}
            <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-xl px-2.5 py-1 text-xs">
              <span className="text-slate-400 font-mono text-[11px]">Show:</span>
              {[10, 25, 50].map((limit) => (
                <button
                  key={limit}
                  onClick={() => setRowLimit(limit)}
                  className={`px-2 py-0.5 rounded-lg font-mono text-xs transition-colors ${
                    rowLimit === limit
                      ? "bg-slate-900 text-white font-semibold shadow-xs"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  {limit}
                </button>
              ))}
            </div>

            <button
              onClick={handleExportPreviewCSV}
              className="flex items-center gap-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 px-3 py-1.5 rounded-xl text-xs font-medium shadow-xs transition-colors"
            >
              <Download className="w-3.5 h-3.5 text-slate-500" />
              <span>Export CSV</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tabular Preview */}
      <div className="bg-white/80 backdrop-blur-md border border-slate-200/80 rounded-3xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto max-h-[620px]">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-50/95 sticky top-0 z-10 border-b border-slate-200 font-mono uppercase tracking-wider text-slate-500 backdrop-blur-sm">
              <tr>
                <th className="py-3 px-3.5 border-r border-slate-200 text-center w-12 bg-slate-50">
                  #
                </th>
                {columnNames.map((colName) => (
                  <th
                    key={colName}
                    className="py-3 px-3.5 border-r border-slate-200 whitespace-nowrap font-medium text-slate-800"
                  >
                    <div className="flex flex-col gap-0.5">
                      <span>{colName}</span>
                      <span className="text-[10px] font-mono lowercase text-slate-400 font-normal">
                        {columnMetaMap[colName] || "object"}
                      </span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {filteredRows.length > 0 ? (
                filteredRows.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-2.5 px-3 text-center text-slate-400 border-r border-slate-200 bg-slate-50/50 font-semibold select-none text-[11px]">
                      {rIdx + 1}
                    </td>
                    {columnNames.map((colName) => {
                      const val = row[colName];
                      const isNull = val === null || val === undefined;
                      return (
                        <td
                          key={colName}
                          className={`py-2.5 px-3.5 border-r border-slate-100 whitespace-nowrap text-xs ${
                            isNull
                              ? "text-slate-400 italic bg-amber-50/30"
                              : "text-slate-700"
                          }`}
                        >
                          {isNull ? (
                            <span className="text-[10px] text-amber-700 bg-amber-50 border border-amber-200/60 px-1.5 py-0.5 rounded">
                              null
                            </span>
                          ) : typeof val === "boolean" ? (
                            <span
                              className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${
                                val
                                  ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                                  : "bg-rose-50 text-rose-700 border border-rose-200"
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
                    className="text-center py-12 text-sm text-slate-400 font-normal"
                  >
                    No preview records match query "{searchTerm}".
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
