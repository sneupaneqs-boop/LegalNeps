/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // lets the stubbed-API test run `next dev` without touching the production build in .next
  distDir: process.env.NEXT_DIST_DIR || ".next",
};

module.exports = nextConfig;
