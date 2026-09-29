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
};

export type ChatResponse = {
  answer: string;
  language: "en" | "ne";
  sources: Source[];
  llm_used: boolean;
  cached?: boolean;
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
  onMeta: (m: { language: "en" | "ne"; sources: Source[] }) => void;
  onDelta: (text: string) => void;
};

// Streams the answer (NDJSON): sources first, then text as it's written.
// Resolves with the final (citation-normalised) answer.
export async function streamChatMessage(
  message: string,
  language: "en" | "ne",
  handlers: StreamHandlers,
  history: Turn[] = []
): Promise<{ answer: string; llm_used: boolean }> {
  const controller = new AbortController();
  // The server sends sources within ~10s (longer if it was asleep) and caps the answer at ~60s;
  // if nothing arrives in time, fail instead of "thinking" forever.
  let timer = setTimeout(() => controller.abort(), 45_000);
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
        else if (ev.type === "done") return { answer: ev.answer, llm_used: ev.llm_used };
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
