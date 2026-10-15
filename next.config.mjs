/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // In local development, proxy API requests to the local FastAPI backend.
    // In production on Vercel, requests to /api/* are handled directly by Vercel serverless routing
    // configured in vercel.json without Next.js truncating the path.
    if (process.env.NODE_ENV === "development") {
      return [
        {
          source: "/api/:path*",
          destination: "http://127.0.0.1:8000/api/:path*",
        },
      ];
    }
    if (process.env.FASTAPI_URL) {
      return [
        {
          source: "/api/:path*",
          destination: `${process.env.FASTAPI_URL}/api/:path*`,
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
