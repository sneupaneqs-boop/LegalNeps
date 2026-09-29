export type Source = {
  n: number;
  id: string;
  category: string;
  doc_type?: string | null;
  topic: string;
  title: string;
  citation: string;
  snippet: string;
  score: number;
  url?: string | null;
  slug?: string | null;
  section?: string | null;
  status?: string | null;
  pinned?: boolean;
  stale?: boolean;
  decided_bs?: number | null;
  governing_law_bs?: number | null;
};

// A curated action plan that matched the question (shown above the answer).
export type PlaybookCard = {
  id: string;
  issue: Bilingual;
  fact_questions: Bilingual[];
  forum?: Bilingual | null;
  limitation?: Bilingual | null;
};

// Deterministic citation check of the answer, computed server-side.
export type Verification = {
  claims: number;
  supported: number;
  unverified: { text: string; reason: string }[];
  cited_laws: number;
  cited_precedents: number;
};

export type ChatResponse = {
  answer: string;
  language: "en" | "ne";
  sources: Source[];
  llm_used: boolean;
  cached?: boolean;
  playbook?: PlaybookCard | null;
  verification?: Verification | null;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type SearchResponse = { query: string; results: Source[] };

export async function search(
  q: string,
  opts: { category?: "law" | "precedent"; docType?: string; status?: "in_force" | "bill" | "unknown"; lang?: "en" | "ne" } = {}
): Promise<SearchResponse> {
  const params = new URLSearchParams({ q, k: "20", lang: opts.lang || "ne" });
  if (opts.category) params.set("category", opts.category);
  if (opts.docType) params.set("doc_type", opts.docType);
  if (opts.status) params.set("status", opts.status);
  const res = await fetch(`${API_URL}/api/search?${params.toString()}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Request failed with status ${res.status}`);
  return res.json();
}

export type Amendment = { name: string; date_bs: string };

export type LawSectionSummary = {
  id: string;
  section: string | null;
  title_ne: string | null;
  title_en: string | null;
  snippet: string;
};

export type LawDoc = {
  slug: string;
  doc_title_ne: string | null;
  doc_title_en: string | null;
  doc_type: string | null;
  status: string;
  enacted_bs: string | null;
  amended_by: Amendment[];
  consolidated_upto: string | null;
  url: string | null;
  sections: LawSectionSummary[];
};

export type LawSection = {
  slug: string;
  id: string;
  section: string | null;
  title_ne: string | null;
  title_en: string | null;
  text_ne: string | null;
  text_en: string | null;
  source_ne: string | null;
  source_en: string | null;
  url: string | null;
  doc_title_ne: string | null;
  doc_title_en: string | null;
  doc_type: string | null;
  status: string | null;
  prev: { section: string | null; title_ne: string | null } | null;
  next: { section: string | null; title_ne: string | null } | null;
};

export async function getLawDoc(slug: string): Promise<LawDoc | null> {
  // The corpus is static between deploys, so cache reference pages instead
  // of hitting the backend on every visit - cuts most page loads to a CDN hit.
  const res = await fetch(`${API_URL}/api/law/${encodeURIComponent(slug)}`, { next: { revalidate: 3600 } });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Request failed with status ${res.status}`);
  return res.json();
}

export type SavedResearch = {
  id: string;
  question: string;
  answer: ChatResponse;
  language: string;
  created_at: string;
};

export async function saveResearch(
  accessToken: string,
  question: string,
  answer: ChatResponse,
  language: "en" | "ne"
): Promise<SavedResearch> {
  const res = await fetch(`${API_URL}/api/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
    body: JSON.stringify({ question, answer, language }),
  });
  if (!res.ok) throw new Error(`Request failed with status ${res.status}`);
  return res.json();
}

export async function listSavedResearch(accessToken: string): Promise<SavedResearch[]> {
  const res = await fetch(`${API_URL}/api/research`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Request failed with status ${res.status}`);
  return res.json();
}

export async function deleteSavedResearch(accessToken: string, id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/research/${encodeURIComponent(id)}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (!res.ok && res.status !== 404) throw new Error(`Request failed with status ${res.status}`);
}

export type Bilingual = { en: string; ne: string };

export type PlaybookSummary = { id: string; area: string | null; issue: Bilingual };

export type ResolvedProvision = {
  law_title_ne: string;
  section: string | null;
  slug: string;
  citation: string;
  url: string | null;
  status: string | null;
  note: Partial<Bilingual>;
};

export type Playbook = {
  id: string;
  area: string | null;
  issue: Bilingual;
  fact_questions: Bilingual[];
  provisions: ResolvedProvision[];
  evidence: Bilingual[];
  forum: Bilingual;
  limitation: { note: Bilingual; provision: ResolvedProvision | null };
  next_steps: Bilingual[];
  template_link: string | null;
};

export async function listPlaybooks(): Promise<PlaybookSummary[]> {
  const res = await fetch(`${API_URL}/api/playbooks`, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error(`Request failed with status ${res.status}`);
  return res.json();
}

export async function getPlaybook(id: string): Promise<Playbook | null> {
  const res = await fetch(`${API_URL}/api/playbooks/${encodeURIComponent(id)}`, { next: { revalidate: 3600 } });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Request failed with status ${res.status}`);
  return res.json();
}

export async function getLawSection(slug: string, section: string): Promise<LawSection | null> {
  const res = await fetch(
    `${API_URL}/api/law/${encodeURIComponent(slug)}/${encodeURIComponent(section)}`,
    { next: { revalidate: 3600 } }
  );
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Request failed with status ${res.status}`);
  return res.json();
}

export type Turn = { role: "user" | "bot"; text: string };

// The hosted backend sleeps when idle and needs up to a minute to wake;
// ping it as soon as the page opens so it's ready by the time a question is sent.
export function warmUp(): void {
  fetch(`${API_URL}/api/health`, { cache: "no-store" }).catch(() => {});
}

export async function sendChatMessage(
  message: string,
  language: "en" | "ne",
  history: Turn[] = []
): Promise<ChatResponse> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 60_000);
  try {
    const res = await fetch(`${API_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, language, history }),
      signal: controller.signal,
    });
    if (!res.ok) {
      throw new Error(`Request failed with status ${res.status}`);
    }
    return res.json();
  } finally {
    clearTimeout(timer);
  }
}

export type StreamHandlers = {
  onMeta: (m: { language: "en" | "ne"; sources: Source[]; playbook?: PlaybookCard | null }) => void;
  onDelta: (text: string) => void;
};

// Streams the answer (NDJSON): sources first, then text as it's written.
// Resolves with the final (citation-normalised) answer.
export async function streamChatMessage(
  message: string,
  language: "en" | "ne",
  handlers: StreamHandlers,
  history: Turn[] = []
): Promise<{ answer: string; llm_used: boolean; verification?: Verification | null }> {
  const controller = new AbortController();
  // The server sends sources within ~10s (longer if it was asleep) and caps the answer at ~60s;
  // if nothing arrives in time, fail instead of "thinking" forever.
  // 90s: a Render free instance waking from sleep can take ~45s before the first byte
  let timer = setTimeout(() => controller.abort(), 90_000);
  try {
    const res = await fetch(`${API_URL}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, language, history }),
      signal: controller.signal,
    });
    if (!res.ok || !res.body) throw new Error(`Request failed with status ${res.status}`);
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      let nl: number;
      while ((nl = buf.indexOf("\n")) >= 0) {
        const line = buf.slice(0, nl).trim();
        buf = buf.slice(nl + 1);
        if (!line) continue;
        const ev = JSON.parse(line);
        if (ev.type === "meta") {
          clearTimeout(timer);
          timer = setTimeout(() => controller.abort(), 90_000);
          handlers.onMeta(ev);
        }
        else if (ev.type === "delta") handlers.onDelta(ev.text);
        else if (ev.type === "done") return { answer: ev.answer, llm_used: ev.llm_used, verification: ev.verification };
        else if (ev.type === "error") throw new Error("stream error");
      }
    }
    throw new Error("stream ended early");
  } catch (e) {
    if (controller.signal.aborted) throw new Error("timeout");
    throw e;
  } finally {
    clearTimeout(timer);
  }
}

// ===========================================================================
// Feature APIs: drafting, matters, calculators, compliance, account.
// Everything below is additive; the exports above are unchanged.
// ===========================================================================

/** Error thrown by the helpers below; `status` is the HTTP status (0 = network failure). */
export class ApiError extends Error {
  status: number;
  detail: string;
  constructor(status: number, detail: string) {
    super(detail || `Request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function errorFromResponse(res: Response): Promise<ApiError> {
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

type CallOpts = {
  token?: string;
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: unknown;
  form?: FormData;
  signal?: AbortSignal;
};

async function call(path: string, opts: CallOpts = {}): Promise<Response> {
  const headers: Record<string, string> = {};
  if (opts.token) headers.Authorization = `Bearer ${opts.token}`;
  let body: BodyInit | undefined;
  if (opts.form) body = opts.form;
  else if (opts.body !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(opts.body);
  }
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, { method: opts.method || "GET", headers, body, cache: "no-store", signal: opts.signal });
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") throw e;
    throw new ApiError(0, "network error");
  }
  if (!res.ok) throw await errorFromResponse(res);
  return res;
}

async function callJson<T>(path: string, opts: CallOpts = {}): Promise<T> {
  const res = await call(path, opts);
  return res.json() as Promise<T>;
}

const enc = encodeURIComponent;

// ---- drafting -------------------------------------------------------------

export type DraftFieldType = "text" | "textarea" | "number" | "date" | string;

export type DraftingField = {
  id: string;
  label: Bilingual;
  type: DraftFieldType;
  required: boolean;
  help: Bilingual | null;
};

export type DraftingTemplateSummary = { id: string; title: Bilingual; description: Bilingual };

export type DraftingTemplateDetail = DraftingTemplateSummary & {
  fields: DraftingField[];
  provisions: ResolvedProvision[];
};

export type DraftAnswers = Record<string, string>;

export type SavedDraft = {
  id: string;
  template_id: string;
  title: string | null;
  language: "en" | "ne";
  answers: DraftAnswers;
  created_at: string;
  updated_at: string;
};

export type DraftVersion = {
  id: string;
  version_number: number;
  language: "en" | "ne";
  answers: DraftAnswers;
  created_at: string;
};

export const listDraftingTemplates = () => callJson<DraftingTemplateSummary[]>("/api/drafting/templates");

export const getDraftingTemplate = (id: string) =>
  callJson<DraftingTemplateDetail>(`/api/drafting/templates/${enc(id)}`);

/** Renders the DOCX on the server and returns it as a Blob (throws ApiError on 400 with the missing-field detail). */
export async function renderDraftDocx(templateId: string, answers: DraftAnswers, language: "en" | "ne"): Promise<Blob> {
  const res = await call(`/api/drafting/templates/${enc(templateId)}/draft`, {
    method: "POST",
    body: { language, answers },
  });
  return res.blob();
}

export async function aiFillField(
  accessToken: string,
  templateId: string,
  req: { field_id: string; hint: string; language: "en" | "ne"; other_answers: DraftAnswers }
): Promise<string> {
  const out = await callJson<{ text: string }>(`/api/drafting/templates/${enc(templateId)}/ai-fill`, {
    token: accessToken,
    method: "POST",
    body: req,
  });
  return out.text;
}

export const createDraft = (
  accessToken: string,
  d: { template_id: string; language: "en" | "ne"; answers: DraftAnswers; title?: string | null }
) => callJson<SavedDraft>("/api/drafting/drafts", { token: accessToken, method: "POST", body: d });

export const listDrafts = (accessToken: string) =>
  callJson<SavedDraft[]>("/api/drafting/drafts", { token: accessToken });

export const getDraft = (accessToken: string, id: string) =>
  callJson<SavedDraft>(`/api/drafting/drafts/${enc(id)}`, { token: accessToken });

export const updateDraft = (
  accessToken: string,
  id: string,
  d: { template_id: string; language: "en" | "ne"; answers: DraftAnswers; title?: string | null }
) => callJson<SavedDraft>(`/api/drafting/drafts/${enc(id)}`, { token: accessToken, method: "PUT", body: d });

export async function deleteDraft(accessToken: string, id: string): Promise<void> {
  await call(`/api/drafting/drafts/${enc(id)}`, { token: accessToken, method: "DELETE" });
}

export const listDraftVersions = (accessToken: string, id: string) =>
  callJson<DraftVersion[]>(`/api/drafting/drafts/${enc(id)}/versions`, { token: accessToken });

// ---- matters --------------------------------------------------------------

export type Matter = {
  id: string;
  client_name: string;
  facts: string | null;
  status: "open" | "closed" | string;
  created_at: string;
  updated_at: string;
};

export type MatterNote = { id: string; body: string; created_at: string };

export type MatterTask = {
  id: string;
  title: string;
  done: boolean;
  due_date: string | null;
  created_at: string;
  updated_at: string;
};

export type MatterFile = {
  id: string;
  filename: string;
  content_type: string | null;
  size_bytes: number | null;
  created_at: string;
};

/** Server-side upload limit for matter files. */
export const MATTER_FILE_MAX_BYTES = 20 * 1024 * 1024;

export const listMatters = (t: string) => callJson<Matter[]>("/api/matters", { token: t });
export const createMatter = (t: string, m: { client_name: string; facts?: string | null }) =>
  callJson<Matter>("/api/matters", { token: t, method: "POST", body: m });
export const getMatter = (t: string, id: string) => callJson<Matter>(`/api/matters/${enc(id)}`, { token: t });
export const updateMatter = (
  t: string,
  id: string,
  m: { client_name?: string; facts?: string | null; status?: "open" | "closed" }
) => callJson<Matter>(`/api/matters/${enc(id)}`, { token: t, method: "PUT", body: m });
export async function deleteMatter(t: string, id: string): Promise<void> {
  await call(`/api/matters/${enc(id)}`, { token: t, method: "DELETE" });
}

export const listMatterNotes = (t: string, id: string) =>
  callJson<MatterNote[]>(`/api/matters/${enc(id)}/notes`, { token: t });
export const createMatterNote = (t: string, id: string, body: string) =>
  callJson<MatterNote>(`/api/matters/${enc(id)}/notes`, { token: t, method: "POST", body: { body } });
export async function deleteMatterNote(t: string, id: string, noteId: string): Promise<void> {
  await call(`/api/matters/${enc(id)}/notes/${enc(noteId)}`, { token: t, method: "DELETE" });
}

export const listMatterTasks = (t: string, id: string) =>
  callJson<MatterTask[]>(`/api/matters/${enc(id)}/tasks`, { token: t });
export const createMatterTask = (t: string, id: string, task: { title: string; due_date?: string | null }) =>
  callJson<MatterTask>(`/api/matters/${enc(id)}/tasks`, { token: t, method: "POST", body: task });
export const updateMatterTask = (
  t: string,
  id: string,
  taskId: string,
  patch: { title?: string; done?: boolean; due_date?: string | null }
) => callJson<MatterTask>(`/api/matters/${enc(id)}/tasks/${enc(taskId)}`, { token: t, method: "PUT", body: patch });
export async function deleteMatterTask(t: string, id: string, taskId: string): Promise<void> {
  await call(`/api/matters/${enc(id)}/tasks/${enc(taskId)}`, { token: t, method: "DELETE" });
}

export const listMatterFiles = (t: string, id: string) =>
  callJson<MatterFile[]>(`/api/matters/${enc(id)}/files`, { token: t });
export function uploadMatterFile(t: string, id: string, file: File): Promise<MatterFile> {
  const form = new FormData();
  form.append("file", file);
  return callJson<MatterFile>(`/api/matters/${enc(id)}/files`, { token: t, method: "POST", form });
}
/** Returns a short-lived signed URL the browser can open. */
export async function getMatterFileUrl(t: string, id: string, fileId: string): Promise<string> {
  const out = await callJson<{ url: string }>(`/api/matters/${enc(id)}/files/${enc(fileId)}/download`, { token: t });
  return out.url;
}
export async function deleteMatterFile(t: string, id: string, fileId: string): Promise<void> {
  await call(`/api/matters/${enc(id)}/files/${enc(fileId)}`, { token: t, method: "DELETE" });
}

// ---- calculators (public) ---------------------------------------------------

export type BsDate = { year: number; month: number; day: number };
export type DateConversion = { bs: BsDate; ad: string };

export type LimitationResult = {
  claim_type: string;
  trigger_date: string;
  deadline: string;
  days_remaining: number;
  is_time_barred: boolean;
  note: Bilingual;
  provision: ResolvedProvision;
};

export type CourtFeeResult = {
  claim_value: number;
  filing_fee_npr: number;
  filing_fee_provision: ResolvedProvision;
  court_fee_npr: number;
  court_fee_provision: ResolvedProvision;
  total_npr: number;
};

export type AppealFeeResult = { disputed_value: number; appeal_fee_npr: number; provision: ResolvedProvision };
export type GratuityResult = { amount_npr: number; provision: ResolvedProvision };
export type NoticeResult = { notice_period_days: number; pay_in_lieu_npr: number; provision: ResolvedProvision };
export type SeveranceResult = { amount_npr: number; provision: ResolvedProvision };

const qs = (o: Record<string, string | number>) =>
  new URLSearchParams(Object.entries(o).map(([k, v]) => [k, String(v)])).toString();

export const bsToAd = (year: number, month: number, day: number) =>
  callJson<DateConversion>(`/api/calculators/date/bs-to-ad?${qs({ year, month, day })}`);
export const adToBs = (date: string) => callJson<DateConversion>(`/api/calculators/date/ad-to-bs?${qs({ date })}`);
export const listClaimTypes = () => callJson<string[]>("/api/calculators/limitation/claim-types");
export const checkLimitation = (claim_type: string, trigger_date: string) =>
  callJson<LimitationResult>(`/api/calculators/limitation?${qs({ claim_type, trigger_date })}`);
export const estimateCourtFee = (claim_value: number) =>
  callJson<CourtFeeResult>(`/api/calculators/court-fee?${qs({ claim_value })}`);
export const estimateAppealFee = (disputed_value: number) =>
  callJson<AppealFeeResult>(`/api/calculators/court-fee/appeal?${qs({ disputed_value })}`);
export const calcGratuity = (basic_monthly_pay: number, months_of_service: number) =>
  callJson<GratuityResult>(`/api/calculators/labour/gratuity?${qs({ basic_monthly_pay, months_of_service })}`);
export const calcNotice = (service_days: number, daily_wage: number) =>
  callJson<NoticeResult>(`/api/calculators/labour/notice?${qs({ service_days, daily_wage })}`);
export const calcSeverance = (basic_monthly_pay: number, years_of_service: number) =>
  callJson<SeveranceResult>(`/api/calculators/labour/severance?${qs({ basic_monthly_pay, years_of_service })}`);

// ---- compliance ---------------------------------------------------------------

export type EntityType = "private_limited" | "public_limited" | "partnership" | "sole_proprietorship";

export type CompanyProfileInput = {
  company_name: string;
  entity_type: EntityType;
  pan_vat_registered: boolean;
  has_employees: boolean;
  reminder_email: string | null;
};

export type CompanyProfile = CompanyProfileInput & {
  id: string;
  created_at: string;
  updated_at: string;
};

export type ObligationDue = {
  id: string;
  title_en: string;
  title_ne: string;
  category: string;
  frequency: string;
  citation: string;
  source_url: string | null;
  period: string;
  due_date_bs: string;
  due_date_ad: string;
  days_remaining: number;
};

export type UpcomingObligations = { company_name: string; obligations: ObligationDue[] };

/** Resolves to null when the user has no company profile yet (the API answers 404). */
export async function getCompanyProfile(t: string): Promise<CompanyProfile | null> {
  try {
    return await callJson<CompanyProfile>("/api/company-profile", { token: t });
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}
export const saveCompanyProfile = (t: string, p: CompanyProfileInput) =>
  callJson<CompanyProfile>("/api/company-profile", { token: t, method: "PUT", body: p });
export const listUpcomingObligations = (t: string, withinDays: number) =>
  callJson<UpcomingObligations>(`/api/obligations/upcoming?${qs({ within_days: withinDays })}`, { token: t });

// ---- account --------------------------------------------------------------------

export type LlmUsage = {
  id: string;
  endpoint: string;
  tier: string;
  provider: string | null;
  model: string | null;
  prompt_version: string | null;
  input_tokens: number | null;
  output_tokens: number | null;
  cost_usd: number;
  flagged_injection: boolean;
  created_at: string;
};

export const listLlmUsage = (t: string, limit = 100) =>
  callJson<LlmUsage[]>(`/api/llm-usage?${qs({ limit })}`, { token: t });
