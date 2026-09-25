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
};

export type ChatResponse = {
  answer: string;
  language: "en" | "ne";
  sources: Source[];
  llm_used: boolean;
  cached?: boolean;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function sendChatMessage(
  message: string,
  language: "en" | "ne"
): Promise<ChatResponse> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 60_000);
  try {
    const res = await fetch(`${API_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, language }),
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
  handlers: StreamHandlers
): Promise<{ answer: string; llm_used: boolean }> {
  const controller = new AbortController();
  // The server sends sources within ~10s and caps the whole answer at ~60s;
  // if nothing arrives in time, fail instead of "thinking" forever.
  let timer = setTimeout(() => controller.abort(), 25_000);
  try {
    const res = await fetch(`${API_URL}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, language }),
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
