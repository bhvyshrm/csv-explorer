"use client";

import React, { useState } from "react";
import { Sparkles, Menu, X, ArrowRight, BarChart2 } from "lucide-react";

interface NavbarProps {
  onStartExploring: () => void;
  onNavigateSection: (sectionId: string) => void;
}

export default function Navbar({ onStartExploring, onNavigateSection }: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { label: "Home", id: "hero" },
    { label: "Explore Data", id: "quick-start" },
    { label: "Formats", id: "format-grid" },
    { label: "Capabilities", id: "capabilities" },
    { label: "How It Works", id: "how-it-works" },
    { label: "Privacy & Trust", id: "privacy" },
  ];

  const handleLinkClick = (id: string) => {
    onNavigateSection(id);
    setMobileMenuOpen(false);
  };

  return (
    <nav className="w-full bg-white/75 backdrop-blur-md border border-white/80 rounded-2xl px-6 py-3.5 shadow-sm transition-all sticky top-4 z-40">
      <div className="flex items-center justify-between">
        {/* Brand Logo & Name */}
        <div
          onClick={() => handleLinkClick("hero")}
          className="flex items-center gap-3 cursor-pointer group select-none"
        >
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-slate-900 to-indigo-900 flex items-center justify-center text-white shadow-md shadow-indigo-950/10 group-hover:scale-105 transition-transform">
            <BarChart2 className="w-5 h-5 text-indigo-200" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-slate-900 tracking-tight">Analytix</span>
              <span className="text-[10px] bg-emerald-50 text-emerald-700 font-semibold px-2 py-0.5 rounded-full border border-emerald-200/60 font-mono">
                Free to use
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-normal hidden sm:block">
              Explore data. Discover insights.
            </p>
          </div>
        </div>

        {/* Desktop Navigation Links */}
        <div className="hidden lg:flex items-center gap-1.5 text-sm font-medium text-slate-600">
          {navLinks.map((link) => (
            <button
              key={link.id}
              onClick={() => handleLinkClick(link.id)}
              className="px-3.5 py-1.5 rounded-lg hover:text-slate-900 hover:bg-slate-100/70 transition-colors"
            >
              {link.label}
            </button>
          ))}
        </div>

        {/* CTA Button */}
        <div className="hidden sm:flex items-center gap-3">
          <button
            onClick={onStartExploring}
            className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-full text-xs font-semibold shadow-sm hover:shadow transition-all group"
          >
            <span>Start Exploring</span>
            <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </div>

        {/* Mobile Hamburger Toggle */}
        <div className="lg:hidden flex items-center gap-2">
          <button
            onClick={onStartExploring}
            className="sm:hidden flex items-center gap-1 bg-slate-900 text-white px-3 py-1.5 rounded-full text-xs font-medium"
          >
            <span>Explore</span>
          </button>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-slate-600 hover:text-slate-900 rounded-lg hover:bg-slate-100/80 transition-colors"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="lg:hidden mt-4 pt-3 border-t border-slate-200/80 space-y-1.5 animate-in fade-in slide-in-from-top-2 duration-150">
          {navLinks.map((link) => (
            <button
              key={link.id}
              onClick={() => handleLinkClick(link.id)}
              className="w-full text-left px-3.5 py-2 rounded-lg text-sm font-medium text-slate-700 hover:text-slate-900 hover:bg-slate-100/70 transition-colors"
            >
              {link.label}
            </button>
          ))}
          <div className="pt-2">
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                onStartExploring();
              }}
              className="w-full flex items-center justify-center gap-2 bg-slate-900 text-white py-2.5 rounded-xl text-xs font-semibold shadow-sm"
            >
              <span>Launch Data Workspace</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}
