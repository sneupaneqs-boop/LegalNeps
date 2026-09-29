import { defineConfig } from "@playwright/test";

// Local production build served on 3910:   npm run build && npm run test:e2e
// Unit tests (no browser, no server):      npm run test:unit
// Signed-in UI against a stubbed API:      npm run test:mock   (next dev on 3911, fake Supabase env)
const PORT = 3910;
const MOCK_PORT = 3911;
const mock = process.env.MOCK === "1";
const proxy = process.env.HTTPS_PROXY || process.env.https_proxy;
const API = process.env.NEXT_PUBLIC_API_URL || "https://kanooni-sathi-api.onrender.com";

export default defineConfig({
  testDir: ".",
  timeout: 120_000,
  expect: { timeout: 30_000 },
  fullyParallel: false,
  workers: 1,
  reporter: [["list"]],
  webServer: mock
    ? {
        command: `npx next dev -p ${MOCK_PORT}`,
        url: `http://localhost:${MOCK_PORT}`,
        reuseExistingServer: false,
        timeout: 120_000,
        env: {
          NEXT_DIST_DIR: ".next-mock",
          NEXT_PUBLIC_API_URL: API,
          NEXT_PUBLIC_SUPABASE_URL: "https://fake.supabase.co",
          NEXT_PUBLIC_SUPABASE_ANON_KEY: "fake-anon-key",
        },
      }
    : {
        command: `npx next start -p ${PORT}`,
        url: `http://localhost:${PORT}`,
        reuseExistingServer: true,
        timeout: 60_000,
      },
  use: {
    baseURL: `http://localhost:${mock ? MOCK_PORT : PORT}`,
    // some sandboxes reach the internet through a TLS-inspecting proxy
    ...(proxy ? { proxy: { server: proxy, bypass: "localhost,127.0.0.1" }, ignoreHTTPSErrors: true } : {}),
  },
  projects: [
    { name: "unit", testMatch: "tests/unit/**/*.spec.ts" },
    {
      name: "mobile",
      testMatch: "e2e/**/*.spec.ts",
      use: { viewport: { width: 360, height: 740 }, isMobile: true, hasTouch: true },
    },
    { name: "desktop", testMatch: "e2e/**/*.spec.ts", use: { viewport: { width: 1280, height: 800 } } },
    { name: "mock", testMatch: "e2e-mock/**/*.spec.ts", use: { viewport: { width: 360, height: 740 }, isMobile: true, hasTouch: true } },
  ],
});
