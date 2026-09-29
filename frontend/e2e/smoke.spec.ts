import { BrowserContext, expect, Page, test } from "@playwright/test";

// Runs against the local production build (`npm run build`, served on :3910) and the LIVE API.
// Signed-in flows (matters, compliance data, saved drafts, AI help, account usage) need a real
// Supabase account and are NOT exercised here; the signed-out prompts for those pages are.

const API = (process.env.NEXT_PUBLIC_API_URL || "https://kanooni-sathi-api.onrender.com").replace(/\/$/, "");
const API_WAIT = { timeout: 90_000 }; // the free-tier API can take ~45s to wake up

// The live API only allows its own Vercel origins, so a page served from localhost is blocked by
// CORS. Forward each API call for real (route.fetch) and only add the CORS headers to the answer.
async function allowLocalOrigin(context: BrowserContext) {
  await context.route(`${API}/**`, async (route) => {
    const req = route.request();
    const cors = {
      "access-control-allow-origin": req.headers()["origin"] || "http://localhost:3910",
      "access-control-allow-credentials": "true",
      "access-control-allow-headers": "*",
      "access-control-allow-methods": "GET,POST,PUT,DELETE,OPTIONS",
      "access-control-expose-headers": "*",
    };
    if (req.method() === "OPTIONS") return route.fulfill({ status: 204, headers: cors });
    const res = await route.fetch({ timeout: 100_000 });
    await route.fulfill({ response: res, headers: { ...res.headers(), ...cors } });
  });
}

function collectErrors(page: Page): string[] {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(`pageerror: ${e.message}`));
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(`console.error: ${m.text()}`);
  });
  return errors;
}

async function expectNav(page: Page) {
  const nav = page.getByRole("navigation", { name: "Main navigation" });
  const burger = page.getByRole("button", { name: "Menu" });
  if (await burger.isVisible()) await burger.click(); // phone: links live in the collapsed menu
  for (const label of ["Ask", "Search", "Action Plans", "Draft", "Matters", "Tools", "Compliance"]) {
    await expect(nav.getByRole("link", { name: label, exact: true })).toBeVisible();
  }
  if (await page.getByRole("button", { name: "Close menu" }).isVisible()) {
    await page.getByRole("button", { name: "Close menu" }).click();
  }
}

async function expectNoHorizontalScroll(page: Page) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow, "page scrolls horizontally").toBeLessThanOrEqual(0);
}

const PAGES: { path: string; heading?: RegExp; signedOut?: boolean }[] = [
  { path: "/" },
  { path: "/search" },
  { path: "/action-plans", heading: /Action Plans|Playbook|plans/i },
  { path: "/saved" },
  { path: "/draft", heading: /Drafting Studio/ },
  { path: "/draft/legal_notice_salary", heading: /unpaid salary/i },
  { path: "/matters", heading: /Matters/, signedOut: true },
  { path: "/matters/does-not-exist", signedOut: true },
  { path: "/tools", heading: /Legal Tools/ },
  { path: "/compliance", heading: /Compliance Radar/, signedOut: true },
  { path: "/account", heading: /Account/, signedOut: true },
];

test.beforeEach(async ({ context }) => {
  await allowLocalOrigin(context);
});

// don't fail a finished test because a background request (e.g. the API warm-up ping) is still in flight
test.afterEach(async ({ context }) => {
  await context.unrouteAll({ behavior: "ignoreErrors" });
});

test.describe("every page renders with navigation and no console errors", () => {
  for (const p of PAGES) {
    test(p.path, async ({ page }) => {
      const errors = collectErrors(page);
      const res = await page.goto(p.path);
      expect(res?.status()).toBe(200);
      await expectNav(page);
      if (p.heading) await expect(page.getByRole("heading", { name: p.heading }).first()).toBeVisible(API_WAIT);
      if (p.signedOut) await expect(page.getByTestId("signin-prompt")).toBeVisible();
      await expectNoHorizontalScroll(page);
      await page.waitForLoadState("networkidle").catch(() => {});
      expect(errors, errors.join("\n")).toEqual([]);
    });
  }
});

test("homepage hero text, in both languages", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 2 })).toHaveText(
    "Ask a question. Find the law. Verify it. Know what to do next."
  );
  await page.getByRole("button", { name: "नेपाली" }).click();
  await expect(page.getByRole("heading", { level: 2 })).toHaveText(
    "प्रश्न सोध्नुहोस्। कानून खोज्नुहोस्। पुष्टि गर्नुहोस्। अब के गर्ने थाहा पाउनुहोस्।"
  );
  // the choice is shared with other pages
  await page.goto("/tools");
  await expect(page.getByRole("heading", { name: "कानूनी उपकरण" })).toBeVisible();
});

test.describe("Tools (live API)", () => {
  test("limitation period returns a result with its provision", async ({ page }) => {
    await page.goto("/tools");
    const card = page.getByTestId("calc-limitation");
    await expect(card.getByLabel("Type of claim").locator("option").first()).toBeAttached(API_WAIT);
    await card.getByLabel("Date the time starts (AD)").fill("2024-01-01");
    await card.getByRole("button", { name: "Calculate" }).click();
    const result = page.getByTestId("limitation-result");
    await expect(result).toBeVisible(API_WAIT);
    await expect(result).toContainText("Deadline");
    await expect(result).toContainText("Time-barred"); // 2024 trigger date is long past for any claim type
    await expect(result.locator(".provision")).toContainText("दफा"); // cited section
  });

  test("court fee, appeal fee and labour calculators", async ({ page }) => {
    await page.goto("/tools");
    const fee = page.getByTestId("calc-court-fee");
    await fee.getByLabel("Claim value (NPR)").fill("500000");
    await fee.getByRole("button", { name: "Calculate" }).click();
    await expect(page.getByTestId("court-fee-result")).toContainText("11,700", API_WAIT);
    await expect(page.getByTestId("court-fee-result").locator(".provision").first()).toContainText("दफा");

    const gr = page.getByTestId("calc-gratuity");
    await gr.getByLabel("Basic monthly pay (NPR)").fill("30000");
    await gr.getByLabel("Months of service").fill("60");
    await gr.getByRole("button", { name: "Calculate" }).click();
    await expect(page.getByTestId("gratuity-result")).toContainText("Rs.", API_WAIT);
    await expect(page.getByTestId("gratuity-result").locator(".provision")).toContainText("श्रम ऐन");
  });

  test("BS <-> AD conversion", async ({ page }) => {
    await page.goto("/tools");
    const card = page.getByTestId("calc-date");
    await card.getByLabel("Year").fill("2081");
    await card.getByLabel("Month").fill("1");
    await card.getByLabel("Day").fill("1");
    await card.getByRole("button", { name: "Calculate" }).click();
    await expect(page.getByTestId("date-ad")).toHaveText("2024-04-13", API_WAIT);

    await card.getByRole("button", { name: "AD → BS" }).click();
    await card.getByLabel("AD date", { exact: true }).fill("2024-04-13");
    await card.getByRole("button", { name: "Calculate" }).click();
    await expect(page.getByTestId("date-bs")).toHaveText("2081-01-01", API_WAIT);
  });

  test("Preeti to Unicode converts as you type", async ({ page }) => {
    await page.goto("/tools");
    await page.getByLabel("Preeti text").fill("sfg\"gL ;fyL");
    await expect(page.getByTestId("preeti-output")).toHaveValue("कानूनी साथी");
  });
});

test.describe("Drafting Studio (live API)", () => {
  test("template list loads", async ({ page }) => {
    await page.goto("/draft");
    const cards = page.getByTestId("template-list").locator("a");
    await expect(cards.first()).toBeVisible(API_WAIT);
    expect(await cards.count()).toBeGreaterThanOrEqual(5);
    // signed out: saved drafts are replaced by a sign-in hint
    await expect(page.getByText("Sign in to save drafts and reopen them later.")).toBeVisible();
  });

  test("template page shows 'Based on' provisions and blocks download until required fields are filled", async ({ page }) => {
    await page.goto("/draft/legal_notice_salary");
    await expect(page.getByRole("heading", { name: "Based on" })).toBeVisible(API_WAIT);
    await expect(page.locator(".provision").first()).toContainText("श्रम ऐन");
    await page.getByTestId("download-docx").click();
    await expect(page.getByText("Please fill in the required fields:")).toBeVisible();
  });

  test("DOCX download starts", async ({ page }) => {
    await page.goto("/draft/legal_notice_salary");
    await expect(page.getByLabel("Your full name", { exact: false })).toBeVisible(API_WAIT);
    // fill every required input by its type
    const required = page.locator("input[aria-required='true'], textarea[aria-required='true']");
    const n = await required.count();
    for (let i = 0; i < n; i++) {
      const el = required.nth(i);
      const type = await el.getAttribute("type");
      await el.fill(type === "number" ? "5000" : type === "date" ? "2026-01-01" : "Test value");
    }
    const [download] = await Promise.all([page.waitForEvent("download", API_WAIT), page.getByTestId("download-docx").click()]);
    expect(download.suggestedFilename()).toBe("legal_notice_salary.docx");
    const path = await download.path();
    const { statSync, readFileSync } = await import("node:fs");
    expect(statSync(path).size).toBeGreaterThan(1000);
    expect(readFileSync(path).subarray(0, 2).toString()).toBe("PK"); // .docx is a zip
  });
});
