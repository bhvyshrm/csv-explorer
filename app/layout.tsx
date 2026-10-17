import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Analytix — Explore data. Discover insights.",
  description:
    "Powerful data exploration and reporting, free to use. Inspect datasets, analyze data quality, discover patterns, generate visualizations, and download professional reports.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased selection:bg-indigo-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
