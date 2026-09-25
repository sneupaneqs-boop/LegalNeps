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
  const timer = setTimeout(() => controller.abort(), 90_000);
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
