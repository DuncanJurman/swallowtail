import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  transpilePackages: [],
  experimental: {
    optimizePackageImports: ['lucide-react', '@radix-ui/react-*'],
  },
};

export default nextConfig;
