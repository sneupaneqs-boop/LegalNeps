"use client";

import { useEffect, useRef, useState } from "react";
import ChatMessage, { Message } from "@/components/ChatMessage";
import { saveResearch, sendChatMessage, streamChatMessage, Turn, warmUp } from "@/lib/api";
import { useLang } from "@/lib/LangContext";
import { useAuth } from "@/lib/useAuth";

export default function Home() {
  const { lang, t } = useLang();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const { session } = useAuth();

  useEffect(() => {
    warmUp();
  }, []);

  const nextId = useRef(0);
  const newId = () => `m${nextId.current++}`;

  async function handleSend(preset?: string) {
    const text = (preset ?? input).trim();
    if (!text || loading) return;

    // last few turns so follow-ups ("what about daughters?") are understood
    const history: Turn[] = messages
      .filter((m) => m.text && !m.streaming)
      .slice(-6)
      .map((m) => ({ role: m.role, text: m.text.slice(0, 1500) }));
    setMessages((prev) => [...prev, { id: newId(), role: "user", text }]);
    setInput("");
    setLoading(true);

    const botId = newId();
    const question = text;
    let started = false;
    const update = (patch: Partial<Message>) =>
      setMessages((prev) => prev.map((m) => (m.id === botId ? { ...m, ...patch } : m)));
    try {
      let streamed = "";
      const final = await streamChatMessage(text, lang, {
        onMeta: (meta) => {
          started = true;
          setMessages((prev) => [
            ...prev,
            {
              id: botId, role: "bot", text: "", sources: meta.sources, llmUsed: true, streaming: true, question,
              playbook: meta.playbook ?? null,
            },
          ]);
        },
        onDelta: (piece) => {
          streamed += piece;
          update({ text: streamed });
        },
        // the verified text shown so far was superseded (fallback / late removal): show the final text
        onReplace: (full) => {
          streamed = full;
          update({ text: streamed });
        },
      }, history);
      update({ text: final.answer, llmUsed: final.llm_used, streaming: false, verification: final.verification ?? null });
    } catch (err) {
      const timedOut = err instanceof Error && err.message === "timeout";
      if (timedOut && !started) {
        setMessages((prev) => [...prev, { id: botId, role: "bot", text: t.timeout }]);
      } else if (!started) {
        // streaming unavailable (proxy, old server): fall back to one-shot request
        try {
          const res = await sendChatMessage(text, lang, history);
          setMessages((prev) => [
            ...prev,
            {
              id: botId, role: "bot", text: res.answer, sources: res.sources, llmUsed: res.llm_used, question,
              playbook: res.playbook ?? null, verification: res.verification ?? null,
            },
          ]);
        } catch {
          setMessages((prev) => [...prev, { id: botId, role: "bot", text: t.error }]);
        }
      } else {
        update({ text: t.error, streaming: false });
      }
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  async function handleSaveResearch(m: Message) {
    if (!session) return;
    setMessages((prev) => prev.map((x) => (x.id === m.id ? { ...x, saving: true } : x)));
    try {
      await saveResearch(
        session.access_token,
        m.question || "",
        { answer: m.text, language: lang, sources: m.sources ?? [], llm_used: !!m.llmUsed },
        lang
      );
      setMessages((prev) => prev.map((x) => (x.id === m.id ? { ...x, saving: false, saved: true } : x)));
    } catch {
      setMessages((prev) => prev.map((x) => (x.id === m.id ? { ...x, saving: false } : x)));
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
      <div className="disclaimer">{t.disclaimerBanner}</div>

      <div className="messages">
        {messages.length === 0 && (
          <div className="hero-wrap">
            <h2 className="hero">{t.heroTitle}</h2>
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
          </div>
        )}
        {messages.map((m) => (
          <ChatMessage
            key={m.id}
            message={m}
            lang={lang}
            canSave={!!session}
            onSave={handleSaveResearch}
            onPrefill={(text) => {
              setInput(text);
              inputRef.current?.focus();
            }}
          />
        ))}
        {loading && !messages.some((m) => m.streaming) && (
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
