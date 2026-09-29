import { BrowserContext, expect, test } from "@playwright/test";

// Signed-in UI flows against a STUBBED API and a fake Supabase session.
// This proves the pages' own logic (forms, tabs, confirms, uploads, downloads, request shapes
// and the Bearer token) - it does NOT prove the real backend or a real login work.
// Run:  npx playwright test --project=mock   (starts `next dev` on :3911 with fake Supabase env)

const API = "https://kanooni-sathi-api.onrender.com";
const SUPA = "https://fake.supabase.co";

type Json = Record<string, unknown>;

function makeStore() {
  let seq = 1;
  const id = () => `id-${seq++}`;
  const now = () => new Date().toISOString();
  return {
    id,
    now,
    seen: [] as { method: string; path: string; auth: string | undefined; body: unknown }[],
    matters: [] as Json[],
    notes: {} as Record<string, Json[]>,
    tasks: {} as Record<string, Json[]>,
    files: {} as Record<string, Json[]>,
    drafts: [] as Json[],
    versions: {} as Record<string, Json[]>,
    profile: null as Json | null,
    plan: "pro",
  };
}

async function installStubs(context: BrowserContext, store: ReturnType<typeof makeStore>) {
  await context.addInitScript(() => {
    const exp = Math.floor(Date.now() / 1000) + 7 * 24 * 3600;
    localStorage.setItem(
      "sb-fake-auth-token",
      JSON.stringify({
        access_token: "tok",
        token_type: "bearer",
        expires_in: 604800,
        expires_at: exp,
        refresh_token: "r",
        user: { id: "u1", aud: "authenticated", email: "tester@example.com", app_metadata: {}, user_metadata: {}, created_at: "2026-01-01T00:00:00Z" },
      })
    );
    // deterministic answers for window.confirm
    window.confirm = () => true;
  });

  await context.route(`${SUPA}/**`, async (route) => {
    const url = route.request().url();
    if (url.includes("/rest/v1/profiles")) {
      return route.fulfill({ json: { plan: store.plan }, headers: { "content-type": "application/json" } });
    }
    return route.fulfill({ status: 404, json: {} });
  });

  await context.route(`${API}/**`, async (route) => {
    const req = route.request();
    const cors = {
      "access-control-allow-origin": req.headers()["origin"] || "*",
      "access-control-allow-headers": "*",
      "access-control-allow-methods": "*",
    };
    if (req.method() === "OPTIONS") return route.fulfill({ status: 204, headers: cors });
    const u = new URL(req.url());
    const path = u.pathname.replace(/^\/api/, "");
    let body: unknown = undefined;
    try {
      body = req.postDataJSON();
    } catch {
      body = req.postData() ? "<multipart>" : undefined;
    }
    store.seen.push({ method: req.method(), path, auth: req.headers()["authorization"], body });
    const ok = (data: unknown, status = 200) => route.fulfill({ status, json: data as Json, headers: cors });
    const none = () => route.fulfill({ status: 204, headers: cors });
    const m = req.method();
    let g: RegExpMatchArray | null;

    // ---- passthrough-ish public endpoints
    if (path === "/health") return ok({ status: "ok" });
    if (path === "/drafting/templates" && m === "GET")
      return ok([{ id: "affidavit", title: { en: "Affidavit", ne: "शपथपत्र" }, description: { en: "d", ne: "d" } }]);
    if (path === "/drafting/templates/affidavit" && m === "GET")
      return ok({
        id: "affidavit",
        title: { en: "Affidavit", ne: "शपथपत्र" },
        description: { en: "d", ne: "d" },
        fields: [
          { id: "declarant_name", label: { en: "Name", ne: "नाम" }, type: "text", required: true, help: null },
          { id: "statement_text", label: { en: "Statement", ne: "विवरण" }, type: "textarea", required: true, help: null },
        ],
        provisions: [],
      });
    if (path === "/drafting/templates/affidavit/ai-fill" && m === "POST") return ok({ text: "Expanded formal text." });
    if (path === "/drafting/templates/affidavit/draft" && m === "POST")
      return route.fulfill({
        status: 200,
        body: "PK-fake-docx",
        headers: { ...cors, "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document" },
      });

    if (!req.headers()["authorization"]) return ok({ detail: "sign in required" }, 401);

    // ---- drafts
    if (path === "/drafting/drafts" && m === "GET") return ok(store.drafts);
    if (path === "/drafting/drafts" && m === "POST") {
      const b = body as Json;
      const d = { id: store.id(), template_id: b.template_id, title: b.title ?? null, language: b.language, answers: b.answers, created_at: store.now(), updated_at: store.now() };
      store.drafts.push(d);
      store.versions[d.id] = [{ id: store.id(), version_number: 1, language: b.language, answers: b.answers, created_at: store.now() }];
      return ok(d, 201);
    }
    if ((g = path.match(/^\/drafting\/drafts\/([^/]+)\/versions$/))) return ok(store.versions[g[1]] ?? []);
    if ((g = path.match(/^\/drafting\/drafts\/([^/]+)$/))) {
      const d = store.drafts.find((x) => x.id === g![1]);
      if (m === "GET") return d ? ok(d) : ok({ detail: "draft not found" }, 404);
      if (m === "PUT" && d) {
        const b = body as Json;
        Object.assign(d, { answers: b.answers, language: b.language, title: b.title ?? null, updated_at: store.now() });
        const vs = store.versions[g[1]];
        vs.push({ id: store.id(), version_number: vs.length + 1, language: b.language, answers: b.answers, created_at: store.now() });
        return ok(d);
      }
      if (m === "DELETE") {
        store.drafts = store.drafts.filter((x) => x.id !== g![1]);
        return none();
      }
    }

    // ---- matters
    if (path === "/matters" && m === "GET") return ok(store.matters);
    if (path === "/matters" && m === "POST") {
      const b = body as Json;
      const row = { id: store.id(), client_name: b.client_name, facts: b.facts ?? null, status: "open", created_at: store.now(), updated_at: store.now() };
      store.matters.unshift(row);
      return ok(row, 201);
    }
    if ((g = path.match(/^\/matters\/([^/]+)$/))) {
      const row = store.matters.find((x) => x.id === g![1]);
      if (!row) return ok({ detail: "matter not found" }, 404);
      if (m === "GET") return ok(row);
      if (m === "PUT") {
        const b = body as Json;
        for (const k of ["client_name", "facts", "status"]) if (b[k] !== undefined && b[k] !== null) row[k] = b[k];
        row.updated_at = store.now();
        return ok(row);
      }
      if (m === "DELETE") {
        store.matters = store.matters.filter((x) => x.id !== g![1]);
        return none();
      }
    }
    if ((g = path.match(/^\/matters\/([^/]+)\/(notes|tasks|files)(?:\/([^/]+?))?(\/download)?$/))) {
      const [, mid, kind, itemId, dl] = g;
      const bucket = (store as unknown as Record<string, Record<string, Json[]>>)[kind];
      bucket[mid] ??= [];
      const list = bucket[mid];
      if (dl) return ok({ url: "https://files.example.test/signed/abc" });
      if (!itemId && m === "GET") return ok(list);
      if (!itemId && m === "POST") {
        let row: Json;
        if (kind === "notes") row = { id: store.id(), body: (body as Json).body, created_at: store.now() };
        else if (kind === "tasks") row = { id: store.id(), title: (body as Json).title, done: false, due_date: (body as Json).due_date ?? null, created_at: store.now(), updated_at: store.now() };
        else row = { id: store.id(), filename: "upload.txt", content_type: "text/plain", size_bytes: 12, created_at: store.now() };
        list.unshift(row);
        return ok(row, 201);
      }
      if (itemId && m === "PUT") {
        const row = list.find((x) => x.id === itemId)!;
        for (const [k, v] of Object.entries(body as Json)) if (v !== null && v !== undefined) row[k] = v;
        return ok(row);
      }
      if (itemId && m === "DELETE") {
        bucket[mid] = list.filter((x) => x.id !== itemId);
        return none();
      }
    }

    // ---- compliance + account
    if (path === "/company-profile" && m === "GET")
      return store.profile ? ok(store.profile) : ok({ detail: "no company profile - create one with PUT /company-profile" }, 404);
    if (path === "/company-profile" && m === "PUT") {
      store.profile = { id: store.id(), ...(body as Json), created_at: store.now(), updated_at: store.now() };
      return ok(store.profile);
    }
    if (path === "/obligations/upcoming" && m === "GET") {
      if (!store.profile) return ok({ detail: "no company profile" }, 404);
      return ok({
        company_name: store.profile.company_name,
        obligations: [
          { id: "vat", title_en: "VAT return", title_ne: "मूल्य अभिवृद्धि कर विवरण", category: "tax", frequency: "monthly", citation: "मूल्य अभिवृद्धि कर ऐन, २०५२, दफा 26", source_url: "https://example.test/vat", period: "2083-05", due_date_bs: "2083-06-25", due_date_ad: "2026-10-11", days_remaining: 12 },
          { id: "audit", title_en: "Annual audit filing", title_ne: "वार्षिक लेखापरीक्षण", category: "company", frequency: "yearly", citation: "कम्पनी ऐन, २०६३, दफा 111", source_url: null, period: "2082/83", due_date_bs: "2083-09-30", due_date_ad: "2027-01-13", days_remaining: 106 },
        ],
      });
    }
    if (path === "/llm-usage" && m === "GET")
      return ok([{ id: "u1", endpoint: "/api/drafting/ai-fill", tier: "sonnet", provider: "anthropic", model: "claude-sonnet", prompt_version: "v1", input_tokens: 500, output_tokens: 200, cost_usd: 0.0045, flagged_injection: false, created_at: store.now() }]);

    return ok({ detail: `unstubbed ${m} ${path}` }, 500);
  });
}

test.describe("signed-in flows (stubbed API)", () => {
  let store: ReturnType<typeof makeStore>;
  test.beforeEach(async ({ context }) => {
    store = makeStore();
    await installStubs(context, store);
  });

  test("header shows Account link and email; account page shows plan and usage", async ({ page }) => {
    await page.goto("/account");
    await expect(page.getByTestId("account-email")).toHaveText("tester@example.com");
    await expect(page.getByText("Upgrade coming soon")).toBeVisible();
    await expect(page.getByText("Pro", { exact: true })).toBeVisible();
    await expect(page.getByRole("table")).toContainText("0.0045");
    const nav = page.getByRole("navigation", { name: "Main navigation" });
    const burger = page.getByRole("button", { name: "Menu" });
    if (await burger.isVisible()) await burger.click();
    await expect(nav.getByRole("link", { name: "Account", exact: true })).toBeVisible();
  });

  test("matters: create, edit, tabs, notes, tasks, files, close, delete", async ({ page }) => {
    await page.goto("/matters");
    await page.getByLabel("Client / matter name").fill("Ram Sharma v. Landlord");
    await page.getByLabel(/Facts/).fill("Deposit not returned.");
    await page.getByRole("button", { name: "Create matter" }).click();
    await expect(page.getByTestId("matter-list")).toContainText("Ram Sharma v. Landlord");
    expect(store.seen.every((r) => r.path === "/health" || r.auth === "Bearer tok")).toBe(true);

    await page.getByTestId("matter-list").getByRole("link").first().click();
    await expect(page.getByRole("heading", { name: "Ram Sharma v. Landlord" })).toBeVisible();

    // overview: edit
    await page.getByLabel("Client / matter name").fill("Ram Sharma (renamed)");
    await page.getByRole("button", { name: "Save changes" }).click();
    await expect(page.getByRole("heading", { name: "Ram Sharma (renamed)" })).toBeVisible();

    // notes
    await page.getByRole("tab", { name: "Notes" }).click();
    await page.getByLabel("Notes").fill("Called the landlord.");
    await page.getByRole("button", { name: "Add note" }).click();
    await expect(page.getByText("Called the landlord.")).toBeVisible();
    await page.getByRole("button", { name: "Delete" }).click();
    await expect(page.getByText("Called the landlord.")).toHaveCount(0);

    // tasks
    await page.getByRole("tab", { name: "Tasks" }).click();
    await page.getByLabel("Add task", { exact: true }).fill("File complaint");
    await page.locator("#task-due").fill("2020-01-01");
    await page.getByRole("button", { name: "Add task" }).click();
    await expect(page.getByText("File complaint")).toBeVisible();
    await expect(page.getByText("Overdue")).toBeVisible();
    await page.getByRole("checkbox").check();
    await expect(page.getByText("Overdue")).toHaveCount(0);
    await page.getByRole("button", { name: "Delete" }).click();
    await expect(page.getByText("File complaint")).toHaveCount(0);

    // files: too big is rejected client-side (nothing is sent), small file uploads, download opens the signed URL
    await page.getByRole("tab", { name: "Files" }).click();
    const before = store.seen.filter((r) => r.path.endsWith("/files") && r.method === "POST").length;
    await page.locator("#file-input").setInputFiles({ name: "big.bin", mimeType: "application/octet-stream", buffer: Buffer.alloc(21 * 1024 * 1024) });
    await expect(page.getByText(/larger than 20 MB/)).toBeVisible();
    expect(store.seen.filter((r) => r.path.endsWith("/files") && r.method === "POST").length).toBe(before);
    await page.locator("#file-input").setInputFiles({ name: "upload.txt", mimeType: "text/plain", buffer: Buffer.from("hello world!") });
    await expect(page.getByText("upload.txt")).toBeVisible();
    await page.context().route("https://files.example.test/**", (r) => r.fulfill({ status: 200, contentType: "text/plain", body: "file" }));
    const popup = page.waitForEvent("popup");
    await page.getByRole("button", { name: "Download" }).click();
    expect((await popup).url()).toContain("files.example.test/signed/abc");
    await page.getByRole("button", { name: "Delete" }).click();
    await expect(page.getByText("upload.txt")).toHaveCount(0);

    // close + delete
    await page.getByRole("tab", { name: "Overview" }).click();
    await page.getByRole("button", { name: "Close matter" }).click();
    await expect(page.getByText("Closed", { exact: true }).first()).toBeVisible();
    await page.getByRole("button", { name: "Delete matter" }).click();
    await expect(page).toHaveURL(/\/matters$/);
    await expect(page.getByText("No matters yet")).toBeVisible();
  });

  test("drafting: AI help, save, version history, reopen, download", async ({ page }) => {
    await page.goto("/draft/affidavit");
    await page.getByLabel(/^Name/).fill("Sita Devi");
    await page.getByLabel(/^Statement/).fill("short note");
    await page.getByRole("button", { name: /AI help/ }).click();
    await expect(page.getByLabel(/^Statement/)).toHaveValue("Expanded formal text.");
    const ai = store.seen.find((r) => r.path.endsWith("/ai-fill"))!;
    expect(ai.auth).toBe("Bearer tok");
    expect(ai.body).toMatchObject({ field_id: "statement_text", hint: "short note", other_answers: { declarant_name: "Sita Devi" } });

    await page.getByRole("button", { name: "Save draft" }).click();
    await expect(page.getByText("Draft saved.")).toBeVisible();
    await expect(page).toHaveURL(/\?draft=id-/);
    await page.getByLabel(/^Name/).fill("Sita Devi Thapa");
    await page.getByRole("button", { name: "Save changes" }).click();
    await page.getByText("Version history").click();
    await expect(page.getByText(/Version 2/)).toBeVisible();
    await expect(page.getByText(/Version 1/)).toBeVisible();
    await page.getByRole("button", { name: "Load into form" }).last().click(); // oldest version
    await expect(page.getByLabel(/^Name/)).toHaveValue("Sita Devi");

    const [dl] = await Promise.all([page.waitForEvent("download"), page.getByTestId("download-docx").click()]);
    expect(dl.suggestedFilename()).toBe("affidavit.docx");

    // list + reopen
    await page.goto("/draft");
    await expect(page.getByText("My saved drafts")).toBeVisible();
    await page.getByRole("link", { name: "Reopen" }).click();
    await expect(page.getByLabel(/^Name/)).toHaveValue("Sita Devi Thapa");
  });

  test("compliance: profile, obligations with BS+AD dates, .ics download", async ({ page }) => {
    await page.goto("/compliance");
    await expect(page.getByText("Save your company profile above")).toBeVisible();
    await page.getByLabel("Company name").fill("Himal Traders Pvt. Ltd.");
    await page.getByLabel("Entity type").selectOption("private_limited");
    await page.getByLabel("Registered for PAN / VAT").check();
    await page.getByRole("button", { name: "Save profile" }).click();
    await expect(page.getByText("Profile saved.")).toBeVisible();
    const list = page.getByTestId("obligation-list");
    await expect(list).toContainText("VAT return");
    await expect(list).toContainText("2083-06-25");
    await expect(list).toContainText("2026-10-11");
    await expect(list).toContainText("12 days remaining");
    await expect(list).toContainText("कम्पनी ऐन, २०६३, दफा 111");

    const [dl] = await Promise.all([page.waitForEvent("download"), page.getByTestId("add-to-calendar").click()]);
    expect(dl.suggestedFilename()).toMatch(/\.ics$/);
    const { readFileSync } = await import("node:fs");
    const text = readFileSync(await dl.path(), "utf8");
    expect(text).toContain("BEGIN:VCALENDAR");
    expect((text.match(/BEGIN:VEVENT/g) || []).length).toBe(2);
    expect(text).toContain("DTSTART;VALUE=DATE:20261011");
  });
});
