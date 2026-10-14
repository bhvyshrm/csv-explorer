import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Analytix • Explore data. Discover insights.",
  description:
    "A modern, multi-format exploratory data analysis platform supporting CSV files and multi-sheet Excel workbooks (.xlsx, .xls) built with Next.js, Python, and Plotly.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-primary-text min-h-screen antialiased selection:bg-accent selection:text-white">
        {children}
      </body>
    </html>
  );
}
