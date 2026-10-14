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
        background: "#0A0B10",
        card: "#151824",
        "card-hover": "#1C2133",
        border: "#292E3D",
        accent: "#8B7CFF",
        "accent-secondary": "#4DD8C7",
        "primary-text": "#F5F6FA",
        "muted-text": "#94A3B8",
        warning: "#FFB84D",
        danger: "#FF5C77",
        success: "#4DD8C7",
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
