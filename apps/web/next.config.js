/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  experimental: { cpus: 1 },
  async rewrites() {
    return [{ source: '/api/:path*', destination: `${process.env.API_INTERNAL_URL || 'http://127.0.0.1:8000'}/api/:path*` }];
  },
  async headers() {
    return [{ source: '/:path*', headers: [
      { key: 'X-Content-Type-Options', value: 'nosniff' },
      { key: 'Referrer-Policy', value: 'same-origin' },
      { key: 'X-Frame-Options', value: 'DENY' },
    ] }];
  },
};
module.exports = nextConfig;
