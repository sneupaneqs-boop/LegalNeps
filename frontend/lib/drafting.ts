// Typed client + UI strings for the drafting catalogue (categories, official
// formats, PDF export). Kept separate from lib/api.ts on purpose - the older
// drafting exports there are unchanged and still used for saved drafts.

import { ApiError, Bilingual, DraftAnswers, ResolvedProvision } from "@/lib/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type DraftCategory = "court" | "police" | "office" | "deeds" | "notices";

/** Display order of the groups on the template list. */
export const DRAFT_CATEGORIES: DraftCategory[] = ["court", "police", "office", "deeds", "notices"];

export type DraftKind = "official" | "standard";

/** Where a template's layout comes from. `official` names a schedule (with the page of the official PDF);
 * `standard` carries a note saying no schedule prescribes the form. */
export type DraftSource = {
  law_title_ne: string;
  law_title_en?: string | null;
  schedule?: string | null;
  relates_to?: string | null;
  form_title?: string | null;
  url?: string | null;
  page?: number | null;
  note?: Bilingual | null;
};

export type DraftFieldOption = { value: string; label: Bilingual };

export type DraftField = {
  id: string;
  label: Bilingual;
  type: "text" | "textarea" | "number" | "date" | "select" | string;
  required: boolean;
  help: Bilingual | null;
  options?: DraftFieldOption[] | null;
  default?: string | number | null;
};

export type DraftTemplateSummary = {
  id: string;
  title: Bilingual;
  description: Bilingual;
  category: DraftCategory;
  kind: DraftKind;
  source: DraftSource | null;
  languages: ("en" | "ne")[];
  keywords: string[];
};

export type DraftTemplateDetail = DraftTemplateSummary & {
  fields: DraftField[];
  provisions: ResolvedProvision[];
  formats: ("docx" | "pdf")[];
};

export type DraftFormat = "docx" | "pdf";

async function failure(res: Response): Promise<ApiError> {
  let detail = "";
  try {
    const body = await res.json();
    if (typeof body?.detail === "string") detail = body.detail;
    else if (Array.isArray(body?.detail)) detail = body.detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join("; ");
  } catch {
    // not JSON
  }
  return new ApiError(res.status, detail);
}

async function request(path: string, init?: RequestInit): Promise<Response> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, { cache: "no-store", ...init });
  } catch {
    throw new ApiError(0, "network error");
  }
  if (!res.ok) throw await failure(res);
  return res;
}

// An older API (or a test double) may omit the catalogue fields: fall back to plain "standard" templates.
function normalise<T extends Partial<DraftTemplateSummary>>(t: T): T & DraftTemplateSummary {
  return {
    category: "notices",
    kind: "standard",
    source: null,
    languages: ["en", "ne"],
    keywords: [],
    ...t,
  } as T & DraftTemplateSummary;
}

export async function listTemplates(): Promise<DraftTemplateSummary[]> {
  const rows: DraftTemplateSummary[] = await (await request("/api/drafting/templates")).json();
  return rows.map(normalise);
}

export async function getTemplate(id: string): Promise<DraftTemplateDetail> {
  const d = await (await request(`/api/drafting/templates/${encodeURIComponent(id)}`)).json();
  return { formats: ["docx"], ...normalise(d) } as DraftTemplateDetail;
}

/** Renders the drafted document on the server as DOCX or PDF and returns it as a Blob
 * (throws ApiError; a 400 carries the missing-field detail). */
export async function renderDraftFile(
  templateId: string,
  answers: DraftAnswers,
  language: "en" | "ne",
  format: DraftFormat
): Promise<Blob> {
  const res = await request(`/api/drafting/templates/${encodeURIComponent(templateId)}/draft`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ language, answers, format }),
  });
  return res.blob();
}

// ---- search ----------------------------------------------------------------

/** Case-insensitive match over title, description, category label and keywords (both scripts). */
export function templateMatches(tpl: DraftTemplateSummary, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  const hay = [
    tpl.title.en,
    tpl.title.ne,
    tpl.description.en,
    tpl.description.ne,
    tpl.source?.law_title_ne ?? "",
    tpl.source?.law_title_en ?? "",
    tpl.source?.schedule ?? "",
    ...tpl.keywords,
  ]
    .join(" \n ")
    .toLowerCase();
  return q.split(/\s+/).every((word) => hay.includes(word));
}

// ---- strings ---------------------------------------------------------------

type UiStrings = {
  categories: Record<DraftCategory, string>;
  searchLabel: string;
  searchPlaceholder: string;
  noMatches: string;
  officialFormat: string;
  standardFormat: string;
  standardFormatLong: string;
  officialLong: string;
  openOfficial: string;
  page: string;
  formatBoxTitle: string;
  nepaliOnly: string;
  downloadDocx: string;
  downloadPdf: string;
  downloading: string;
  pdfNote: string;
  choose: string;
  formsCount: (n: number) => string;
};

export const draftUi: Record<"en" | "ne", UiStrings> = {
  en: {
    categories: {
      court: "Court",
      police: "Police & criminal",
      office: "Government office",
      deeds: "Deeds & contracts",
      notices: "Notices",
    },
    searchLabel: "Search formats",
    searchPlaceholder: "Search, e.g. plaint, FIR, writ, RTI, power of attorney, फिराद, जाहेरी…",
    noMatches: "No format matches your search.",
    officialFormat: "Official format",
    standardFormat: "Standard format",
    standardFormatLong: "Standard format (not prescribed by a schedule)",
    officialLong: "Official format",
    openOfficial: "Open the official PDF",
    page: "page",
    formatBoxTitle: "Format",
    nepaliOnly: "Prescribed forms exist only in Nepali, so this document is drafted in Nepali.",
    downloadDocx: "Download DOCX",
    downloadPdf: "Download PDF",
    downloading: "Preparing…",
    pdfNote: "PDF is rendered with a bundled Devanagari font; the DOCX opens in Word (uses Kalimati, falling back to Mangal).",
    choose: "— choose —",
    formsCount: (n) => `${n} format${n === 1 ? "" : "s"}`,
  },
  ne: {
    categories: {
      court: "अदालत",
      police: "प्रहरी र फौजदारी",
      office: "सरकारी कार्यालय",
      deeds: "लिखत र सम्झौता",
      notices: "सूचना",
    },
    searchLabel: "ढाँचा खोज्नुहोस्",
    searchPlaceholder: "खोज्नुहोस्, जस्तै: फिराद, जाहेरी, रिट, सूचनाको हक, अख्तियारनामा…",
    noMatches: "तपाईंको खोजीसँग मिल्ने ढाँचा भेटिएन।",
    officialFormat: "आधिकारिक ढाँचा",
    standardFormat: "मानक ढाँचा",
    standardFormatLong: "मानक ढाँचा (अनुसूचीमा तोकिएको होइन)",
    officialLong: "आधिकारिक ढाँचा",
    openOfficial: "आधिकारिक PDF खोल्नुहोस्",
    page: "पृष्ठ",
    formatBoxTitle: "ढाँचा",
    nepaliOnly: "तोकिएका ढाँचा नेपालीमा मात्र छन्, त्यसैले यो कागजात नेपालीमा तयार हुन्छ।",
    downloadDocx: "DOCX डाउनलोड",
    downloadPdf: "PDF डाउनलोड",
    downloading: "तयार हुँदैछ…",
    pdfNote: "PDF मा देवनागरी फन्ट समावेश छ; DOCX वर्डमा खुल्छ (कलिमाटी फन्ट, नभए मंगल)।",
    choose: "— छान्नुहोस् —",
    formsCount: (n) => `${n} ढाँचा`,
  },
};

/** "Official format: <law>, अनुसूची–N" - the line shown on cards and on the template page. */
export function officialLine(src: DraftSource, lang: "en" | "ne"): string {
  const law = lang === "en" && src.law_title_en ? `${src.law_title_en} (${src.law_title_ne})` : src.law_title_ne;
  return `${draftUi[lang].officialFormat}: ${law}${src.schedule ? `, ${src.schedule}` : ""}`;
}
