// API client and helpers for the /tools page: the limitation-period catalog and
// deadline calculator, and the labour / interest / tax / court-fee / date tools.
// Everything here is additive: it does not touch the exports of lib/api.ts.

import { ApiError, Bilingual, ResolvedProvision } from "@/lib/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Calendar = "ad" | "bs";

/** GET a tools endpoint. Empty / undefined params are dropped. Throws ApiError (status 0 = network failure). */
export async function toolGet<T>(path: string, params: Record<string, string | number | boolean | undefined | null> = {}): Promise<T> {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === "") continue;
    qs.set(k, String(v));
  }
  const query = qs.toString();
  let res: Response;
  try {
    res = await fetch(`${API_URL}/api/calculators${path}${query ? `?${query}` : ""}`, { cache: "no-store" });
  } catch {
    throw new ApiError(0, "network error");
  }
  if (!res.ok) {
    let detail = "";
    try {
      const body = await res.json();
      if (typeof body?.detail === "string") detail = body.detail;
      else if (Array.isArray(body?.detail)) detail = body.detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join("; ");
    } catch {
      // not JSON
    }
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

// ---- limitation ---------------------------------------------------------------------------

export type PeriodKind = "fixed" | "none" | "special";
export type PeriodUnit = "days" | "months" | "years";

export type LimitationEntry = {
  id: string;
  category: string;
  name: Bilingual;
  period: { kind: PeriodKind; value?: number; unit?: PeriodUnit; text: Bilingual };
  start: { kind: string; en: string; ne: string; offset_days?: number } | null;
  applies_to: Bilingual | null;
  notes: Bilingual | null;
  long_stop: { value: number; unit: PeriodUnit; start: Bilingual; text: Bilingual } | null;
  keywords: string[];
  needs_review: boolean;
  computable: boolean;
  citation: {
    law_title_ne: string;
    law_en: string | null;
    section: string;
    clause: string | null;
    slug: string | null;
    citation: string | null;
    url: string | null;
    resolved: boolean;
  };
};

export type LimitationCategory = { id: string; name: Bilingual; entries: LimitationEntry[] };

export type GeneralRule = { id: string; text: Bilingual; citation: ResolvedProvision | null };

export type LimitationCatalog = { total: number; categories: LimitationCategory[]; general_rules: GeneralRule[] };

export type BsParts = { year: number; month: number; day: number; iso: string };

export type DeadlineResult = {
  claim_type: string;
  trigger_date: string;
  deadline: string;
  days_remaining: number;
  is_time_barred: boolean;
  note: Bilingual;
  provision: ResolvedProvision;
  name: Bilingual;
  category: string;
  period: { kind: PeriodKind; value?: number; unit?: PeriodUnit; text: Bilingual };
  start: { kind: string; en: string; ne: string; offset_days?: number } | null;
  trigger_date_bs: BsParts;
  deadline_bs: BsParts;
  period_deadline: string;
  long_stop: { deadline: string; deadline_bs: BsParts } | null;
  needs_review: boolean;
  clause: string | null;
  counting_note: Bilingual;
};

export const getLimitationCatalog = () => toolGet<LimitationCatalog>("/limitation/catalog");

export const computeDeadline = (args: { claim_id: string; trigger_date: string; calendar: Calendar; long_stop_date?: string }) =>
  toolGet<DeadlineResult>("/limitation/deadline", args);

// ---- shapes shared by the other tools -----------------------------------------------------------

export type Provisions = { provisions?: ResolvedProvision[]; provision?: ResolvedProvision };

/** Pull the cited provisions out of any tool result (some carry `provision`, most `provisions`). */
export function provisionsOf(result: unknown): ResolvedProvision[] {
  const out: ResolvedProvision[] = [];
  const seen = new Set<string>();
  const walk = (v: unknown, depth: number) => {
    if (!v || typeof v !== "object" || depth > 4) return;
    if (Array.isArray(v)) {
      v.forEach((x) => walk(x, depth + 1));
      return;
    }
    const o = v as Record<string, unknown>;
    if (typeof o.citation === "string" && typeof o.slug === "string") {
      const key = `${o.slug}|${o.section ?? ""}`;
      if (!seen.has(key)) {
        seen.add(key);
        out.push(o as unknown as ResolvedProvision);
      }
      return;
    }
    Object.values(o).forEach((x) => walk(x, depth + 1));
  };
  walk(result, 0);
  return out;
}

/** In-app link to a cited section: /law/<slug>/<section> with the section encoded. */
export function lawHref(p: { slug: string; section: string | null }): string {
  return p.section ? `/law/${p.slug}/${encodeURIComponent(p.section)}` : `/law/${p.slug}`;
}

// ---- BS calendar helpers ----------------------------------------------------------------------------

export const BS_MONTHS_EN = ["Baisakh", "Jestha", "Ashadh", "Shrawan", "Bhadra", "Ashwin", "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra"];
export const BS_MONTHS_NE = ["बैशाख", "जेठ", "असार", "श्रावण", "भदौ", "असोज", "कार्तिक", "मंसिर", "पौष", "माघ", "फागुन", "चैत"];

export function bsIso(y: string, m: string, d: string): string {
  if (!y.trim() || !m.trim() || !d.trim()) return "";
  const yy = Number(y);
  const mm = Number(m);
  const dd = Number(d);
  if (!Number.isInteger(yy) || !Number.isInteger(mm) || !Number.isInteger(dd)) return "";
  return `${String(yy).padStart(4, "0")}-${String(mm).padStart(2, "0")}-${String(dd).padStart(2, "0")}`;
}

export function formatBs(bs: { year: number; month: number; day: number }, lang: "en" | "ne"): string {
  const names = lang === "ne" ? BS_MONTHS_NE : BS_MONTHS_EN;
  return `${bs.day} ${names[bs.month - 1] ?? bs.month} ${bs.year}`;
}

export function formatAd(iso: string, lang: "en" | "ne"): string {
  const d = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString(lang === "ne" ? "ne-NP" : "en-GB", { year: "numeric", month: "short", day: "numeric" });
}

// ---- search --------------------------------------------------------------------------------------------

const DEV_DIGITS = "०१२३४५६७८९";

/** Lower-case, strip Nepali digits to ASCII and collapse whitespace so "६ महिना" finds "6 months"-style queries. */
export function searchForm(s: string): string {
  return s
    .toLowerCase()
    .replace(/[०-९]/g, (c) => String(DEV_DIGITS.indexOf(c)))
    .replace(/\s+/g, " ")
    .trim();
}

export function entryHaystack(e: LimitationEntry, categoryName: Bilingual): string {
  const parts = [
    e.id.replace(/_/g, " "),
    e.name.en,
    e.name.ne,
    e.period.text.en,
    e.period.text.ne,
    e.start?.en ?? "",
    e.start?.ne ?? "",
    e.applies_to?.en ?? "",
    e.applies_to?.ne ?? "",
    e.notes?.en ?? "",
    e.notes?.ne ?? "",
    e.keywords.join(" "),
    e.citation.law_title_ne,
    e.citation.law_en ?? "",
    e.citation.section,
    e.citation.clause ?? "",
    categoryName.en,
    categoryName.ne,
  ];
  return searchForm(parts.join(" | "));
}

/** Every word in the query must appear somewhere in the haystack. */
export function matchesQuery(haystack: string, query: string): boolean {
  const words = searchForm(query).split(" ").filter(Boolean);
  return words.every((w) => haystack.includes(w));
}
