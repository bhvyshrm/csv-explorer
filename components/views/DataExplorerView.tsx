"use client";

import React, { useState, useMemo } from "react";
import { AnalysisPayload } from "@/types/analytix";
import { Search, Download, Filter } from "lucide-react";

interface DataExplorerViewProps {
  data: AnalysisPayload;
}

export default function DataExplorerView({ data }: DataExplorerViewProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");

  const availableTypes = useMemo(() => {
    const types = new Set<string>();
    data.columns.forEach((c) => types.add(c["Inferred Type"]));
    return Array.from(types);
  }, [data.columns]);

  const filteredColumns = useMemo(() => {
    return data.columns.filter((col) => {
      const matchesSearch = col["Column Name"]
        .toLowerCase()
        .includes(searchTerm.toLowerCase());
      const matchesType =
        typeFilter === "all" || col["Inferred Type"] === typeFilter;
      return matchesSearch && matchesType;
    });
  }, [data.columns, searchTerm, typeFilter]);

  const handleExportCSV = () => {
    const headers = [
      "Column Name",
      "Inferred Type",
      "Python dtype",
      "Missing Count",
      "Missing %",
      "Unique Values",
      "Memory (Bytes)",
    ];
    const rows = filteredColumns.map((col) =>
      [
        `"${col["Column Name"]}"`,
        `"${col["Inferred Type"]}"`,
        `"${col["Python dtype"]}"`,
        col["Missing Count"],
        col["Missing %"],
        col["Unique Values"],
        col["Memory (Bytes)"],
      ].join(",")
    );
    const csvContent = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${data.dataset_name}_column_metadata.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const getTypeBadgeClass = (type: string) => {
    switch (type.toLowerCase()) {
      case "numeric":
        return "bg-purple-950/40 text-purple-300 border-purple-800/40";
      case "categorical":
        return "bg-teal-950/40 text-teal-300 border-teal-800/40";
      case "datetime":
        return "bg-blue-950/40 text-blue-300 border-blue-800/40";
      case "boolean":
        return "bg-indigo-950/40 text-indigo-300 border-indigo-800/40";
      default:
        return "bg-zinc-800 text-zinc-300 border-zinc-700";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-card border border-border rounded-xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-primary-text">
              Data Explorer • Column Profiling
            </h1>
            <p className="text-sm text-muted-text mt-0.5">
              Inspect inferred types, null densities, cardinality, and memory allocations.
            </p>
          </div>
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 bg-card-hover border border-border hover:border-accent text-primary-text px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <Download className="w-4 h-4 text-accent" />
            Export Metadata (CSV)
          </button>
        </div>

        {/* Search & Filter Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 mt-5">
          <div className="relative">
            <Search className="w-4 h-4 text-muted-text absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search column name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-background border border-border focus:border-accent text-primary-text pl-9 pr-4 py-2 rounded-lg text-sm outline-none transition-colors"
            />
          </div>

          <div className="relative">
            <Filter className="w-4 h-4 text-muted-text absolute left-3 top-3 pointer-events-none" />
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full bg-background border border-border focus:border-accent text-primary-text pl-9 pr-4 py-2 rounded-lg text-sm outline-none transition-colors appearance-none cursor-pointer"
            >
              <option value="all">All Inferred Types ({data.columns.length})</option>
              {availableTypes.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center justify-end text-xs text-muted-text font-mono">
            Showing {filteredColumns.length} of {data.columns.length} columns
          </div>
        </div>
      </div>

      {/* Metadata Table */}
      <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-background/80 border-b border-border text-xs uppercase tracking-wider text-muted-text font-mono">
              <tr>
                <th className="py-3 px-4">Column Name</th>
                <th className="py-3 px-4">Inferred Type</th>
                <th className="py-3 px-4">Python dtype</th>
                <th className="py-3 px-4 text-right">Missing Count</th>
                <th className="py-3 px-4 text-right">Missing %</th>
                <th className="py-3 px-4 text-right">Unique Values</th>
                <th className="py-3 px-4 text-right">Memory (Bytes)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {filteredColumns.length > 0 ? (
                filteredColumns.map((col, idx) => (
                  <tr
                    key={idx}
                    className="hover:bg-card-hover/60 transition-colors"
                  >
                    <td className="py-3 px-4 font-mono font-medium text-primary-text">
                      {col["Column Name"]}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`text-xs px-2.5 py-0.5 rounded-full border font-mono font-medium ${getTypeBadgeClass(
                          col["Inferred Type"]
                        )}`}
                      >
                        {col["Inferred Type"]}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-xs text-muted-text">
                      {col["Python dtype"]}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-primary-text">
                      {col["Missing Count"]}
                    </td>
                    <td className="py-3 px-4 text-right font-mono">
                      <span
                        className={
                          col["Missing %"] > 0
                            ? "text-warning font-semibold"
                            : "text-muted-text"
                        }
                      >
                        {col["Missing %"].toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-primary-text">
                      {col["Unique Values"].toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-muted-text text-xs">
                      {col["Memory (Bytes)"].toLocaleString()} B
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan={7}
                    className="text-center py-8 text-sm text-muted-text"
                  >
                    No columns match your filter criteria.
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
