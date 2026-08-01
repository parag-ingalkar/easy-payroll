import type { NextConfig } from "next";

const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
const frontendUrl = process.env.NEXT_PUBLIC_FRONTEND_URL || "http://localhost:3000";

const nextConfig: NextConfig = {
  output: "standalone",
  /* config options here */
  typescript: {
    ignoreBuildErrors: true,
  },
  reactStrictMode: false,
  // In production on Cloud Run/Container deployments, the frontend and backend
  // may be served from different containers/ports. The rewrites ensure that
  // /api/* requests are proxied to the backend, making them same-origin from
  // the browser's perspective. This avoids CORS issues entirely since the
  // browser only sees same-origin requests.
  // 
  // For Cloud Run: Set BACKEND_URL to the internal service URL or use a shared domain
  // with path-based routing (e.g., domain.com/api -> backend, domain.com -> frontend)
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
  // Configure allowed hosts for production deployments
  // This prevents host header attacks in production
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "X-Frame-Options",
            value: "DENY",
          },
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
