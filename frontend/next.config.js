/** @type {import('next').NextConfig} */

const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const supabase = process.env.NEXT_PUBLIC_SUPABASE_URL || "";

// Next's hydration needs inline scripts, so script-src keeps 'unsafe-inline';
// the rest is locked down: no framing (clickjacking), no plugins, and the
// browser may only call our own API and Supabase.
const csp = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline'",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self' data:",
  `connect-src 'self' ${api} ${supabase} ${supabase.replace("https://", "wss://")}`.trim(),
  "frame-ancestors 'none'",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
].join("; ");

const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  // lets the stubbed-API test run `next dev` without touching the production build in .next
  distDir: process.env.NEXT_DIST_DIR || ".next",
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "Content-Security-Policy", value: csp },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), payment=()" },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
