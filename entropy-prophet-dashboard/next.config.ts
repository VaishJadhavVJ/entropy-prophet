import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  logging: {
    fetches: { fullUrl: false },
    // suppress 404s from browser extensions hitting localhost
    incomingRequests: { ignore: [/^\/agents\//] },
  },
};

export default nextConfig;
