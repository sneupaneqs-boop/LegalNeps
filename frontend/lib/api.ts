export type Source = {
  id: string;
  category: string;
  topic: string;
  title: string;
  citation: string;
  snippet: string;
  score: number;
};

export type ChatResponse = {
  answer: string;
  language: "en" | "ne";
  sources: Source[];
  llm_used: boolean;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function sendChatMessage(
  message: string,
  language: "en" | "ne"
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, language }),
  });

  if (!res.ok) {
    throw new Error(`Request failed with status ${res.status}`);
  }

  return res.json();
}
