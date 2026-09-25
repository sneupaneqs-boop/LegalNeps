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

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const res = await sendChatMessage(text, lang);
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: res.answer,
          sources: res.sources,
          llmUsed: res.llm_used,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text:
            lang === "en"
              ? "Something went wrong reaching the server. Please try again."
              : "सर्भरसँग जडान गर्दा समस्या भयो। कृपया फेरि प्रयास गर्नुहोस्।",
        },
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
          <div className="empty-state">{t.emptyState}</div>
        )}
        {messages.map((m, i) => (
          <ChatMessage key={i} message={m} lang={lang} />
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
        <button onClick={handleSend} disabled={loading || !input.trim()}>
          {t.send}
        </button>
      </div>
    </div>
  );
}
