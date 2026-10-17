"use client";

import React, { useRef } from "react";
import Navbar from "./Navbar";
import Hero from "./Hero";
import QuickStartUpload from "./QuickStartUpload";
import FormatGrid from "./FormatGrid";
import CapabilitiesGrid from "./CapabilitiesGrid";
import HowItWorks from "./HowItWorks";
import AnalyticsPreview from "./AnalyticsPreview";
import PrivacyTrust from "./PrivacyTrust";
import Footer from "./Footer";

interface HomepageViewProps {
  onStartExploring: () => void;
  onFileUpload: (file: File) => Promise<void>;
  onLoadSample: (endpoint: string) => Promise<void>;
  isLoading: boolean;
  uploadError: string | null;
}

export default function HomepageView({
  onStartExploring,
  onFileUpload,
  onLoadSample,
  isLoading,
  uploadError,
}: HomepageViewProps) {
  const hiddenFileInputRef = useRef<HTMLInputElement>(null);
  const currentFormatAcceptRef = useRef<string>("");

  const scrollToSection = (sectionId: string) => {
    const el = document.getElementById(sectionId);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleSelectFormatUpload = (formatId: string, acceptExtensions: string) => {
    currentFormatAcceptRef.current = acceptExtensions;
    if (hiddenFileInputRef.current) {
      hiddenFileInputRef.current.accept = acceptExtensions;
      hiddenFileInputRef.current.click();
    }
  };

  const handleFormatFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileUpload(e.target.files[0]);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100/70 via-purple-50/60 to-emerald-50/50 p-3 sm:p-6 md:p-8 relative selection:bg-indigo-500 selection:text-white">
      {/* Ambient background soft pastel glow circles */}
      <div className="fixed top-0 left-1/4 w-[500px] h-[500px] bg-purple-200/40 rounded-full blur-3xl pointer-events-none -z-10"></div>
      <div className="fixed bottom-0 right-1/4 w-[600px] h-[600px] bg-emerald-200/30 rounded-full blur-3xl pointer-events-none -z-10"></div>
      <div className="fixed top-1/3 right-10 w-[400px] h-[400px] bg-sky-200/35 rounded-full blur-3xl pointer-events-none -z-10"></div>

      {/* Hidden file input for specific format buttons */}
      <input
        ref={hiddenFileInputRef}
        type="file"
        onChange={handleFormatFileChange}
        className="hidden"
      />

      {/* Main Centered Glass Container (Inspired by Reference Image) */}
      <div className="max-w-6xl mx-auto rounded-[28px] sm:rounded-[36px] bg-white/70 backdrop-blur-2xl border border-white/85 shadow-glass p-4 sm:p-8 md:p-10 relative">
        {/* Navigation Bar */}
        <Navbar
          onStartExploring={onStartExploring}
          onNavigateSection={scrollToSection}
        />

        {/* Secondary Category / Quick Jump Bar */}
        <div className="mt-4 mb-6 hidden md:flex items-center justify-between bg-white/60 backdrop-blur-md border border-white/80 rounded-2xl px-5 py-2.5 text-xs text-slate-600 shadow-xs">
          <div className="flex items-center gap-1 font-mono">
            <span className="text-slate-400">Quick Explorer:</span>
            <button
              onClick={() => scrollToSection("format-grid")}
              className="px-2.5 py-1 rounded-lg hover:bg-slate-100 font-medium hover:text-slate-900 transition-colors"
            >
              CSV
            </button>
            <span className="text-slate-300">•</span>
            <button
              onClick={() => scrollToSection("format-grid")}
              className="px-2.5 py-1 rounded-lg hover:bg-slate-100 font-medium hover:text-slate-900 transition-colors"
            >
              Excel
            </button>
            <span className="text-slate-300">•</span>
            <button
              onClick={() => scrollToSection("format-grid")}
              className="px-2.5 py-1 rounded-lg hover:bg-slate-100 font-medium hover:text-slate-900 transition-colors"
            >
              JSON
            </button>
            <span className="text-slate-300">•</span>
            <button
              onClick={() => scrollToSection("format-grid")}
              className="px-2.5 py-1 rounded-lg hover:bg-slate-100 font-medium hover:text-slate-900 transition-colors"
            >
              Parquet
            </button>
            <span className="text-slate-300">•</span>
            <button
              onClick={() => scrollToSection("format-grid")}
              className="px-2.5 py-1 rounded-lg hover:bg-slate-100 font-medium hover:text-slate-900 transition-colors"
            >
              Logs & Text
            </button>
          </div>

          <div className="flex items-center gap-3 text-[11px] font-mono text-slate-500">
            <span>In-memory computation</span>
            <span>•</span>
            <span className="text-emerald-700 font-semibold">100% Free to use</span>
          </div>
        </div>

        {/* Hero Section */}
        <Hero
          onStartExploring={onStartExploring}
          onExploreFeatures={() => scrollToSection("capabilities")}
        />

        {/* Quick Start Upload Dropzone & Sample Selector */}
        <QuickStartUpload
          onFileUpload={onFileUpload}
          onLoadSample={onLoadSample}
          isLoading={isLoading}
          uploadError={uploadError}
        />

        {/* 6 Format Explorer Cards matching Reference Image */}
        <FormatGrid
          onSelectFormatUpload={handleSelectFormatUpload}
          onSelectSample={onLoadSample}
        />

        {/* What You Can Do (Capabilities Grid) */}
        <CapabilitiesGrid />

        {/* How It Works (3 Steps) */}
        <HowItWorks />

        {/* Analytics Workflow Preview */}
        <AnalyticsPreview onStartExploring={onStartExploring} />

        {/* Privacy, Security & Processing Architecture */}
        <PrivacyTrust />

        {/* Footer with Final CTA */}
        <Footer
          onStartExploring={onStartExploring}
          onNavigateSection={scrollToSection}
        />
      </div>
    </div>
  );
}
