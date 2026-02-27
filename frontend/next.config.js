/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:5002/api/:path*", // Proxy to backend
      },
    ];
  },
};

module.exports = nextConfig;
