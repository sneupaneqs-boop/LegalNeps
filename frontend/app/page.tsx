"use client";

import { useRef, useState } from "react";
import ChatMessage, { Message } from "@/components/ChatMessage";
import { sendChatMessage } from "@/lib/api";
import { Lang, strings } from "@/lib/i18n";

export default function Home() {
  const [lang, setLang] = useState<Lang>("en");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const t = strings[lang];
  const nextId = useRef(0);
  const newId = () => `m${nextId.current++}`;

  async function handleSend(preset?: string) {
    const text = (preset ?? input).trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { id: newId(), role: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const res = await sendChatMessage(text, lang);
      setMessages((prev) => [
        ...prev,
        {
          id: newId(),
          role: "bot",
          text: res.answer,
          sources: res.sources,
          llmUsed: res.llm_used,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { id: newId(), role: "bot", text: t.error },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="page">
      <div className="header">
        <div className="brand">
          <h1>{t.appName}</h1>
          <p>{t.tagline}</p>
        </div>
        <button
          className="lang-toggle"
          onClick={() => setLang(lang === "en" ? "ne" : "en")}
        >
          {t.langToggle}
        </button>
      </div>

      <div className="disclaimer">{t.disclaimerBanner}</div>

      <div className="messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>{t.emptyState}</p>
            <div className="suggestions-label">{t.tryAsking}</div>
            <div className="suggestions">
              {t.suggestions.map((q) => (
                <button key={q} className="suggestion" onClick={() => handleSend(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m) => (
          <ChatMessage key={m.id} message={m} lang={lang} />
        ))}
        {loading && (
          <div className="bubble-row bot">
            <div className="bubble bot">{t.thinking}</div>
          </div>
        )}
      </div>

      <div className="composer">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t.placeholder}
          rows={1}
        />
        <button onClick={() => handleSend()} disabled={loading || !input.trim()}>
          {t.send}
        </button>
      </div>
    </div>
  );
}
