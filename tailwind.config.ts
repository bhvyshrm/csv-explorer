import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F8FAFC",
        card: "#FFFFFF",
        "card-hover": "#F8FAFC",
        border: "#E2E8F0",
        accent: "#6366F1",
        "accent-secondary": "#0D9488",
        "primary-text": "#0F172A",
        "muted-text": "#64748B",
        warning: "#D97706",
        danger: "#E11D48",
        success: "#059669",
        pastel: {
          mint: "#eaf7f0",
          sky: "#edf5fd",
          lavender: "#f3effc",
          peach: "#fef3e9",
          rose: "#fdf0f4",
          teal: "#e9f7f6",
          slate: "#f1f5f9",
        },
        slate: {
          850: "#151e2e",
        },
      },
      boxShadow: {
        glass: "0 20px 60px -15px rgba(0, 0, 0, 0.06), 0 0 0 1px rgba(255, 255, 255, 0.7) inset",
        "glass-card": "0 10px 30px -10px rgba(0, 0, 0, 0.04), 0 0 0 1px rgba(255, 255, 255, 0.8) inset",
        "glass-hover": "0 20px 40px -12px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(255, 255, 255, 0.95) inset",
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
