import { Source } from "@/lib/api";
import { Lang, strings } from "@/lib/i18n";
import { renderAnswer } from "@/lib/markdown";

export type Message = {
  id: string;
  role: "user" | "bot";
  text: string;
  sources?: Source[];
  llmUsed?: boolean;
  streaming?: boolean;
};

export default function ChatMessage({
  message,
  lang,
}: {
  message: Message;
  lang: Lang;
}) {
  const t = strings[lang];
  const isUser = message.role === "user";
  const sources = message.sources ?? [];

  return (
    <div className={`bubble-row ${isUser ? "user" : "bot"}`}>
      <div className={`bubble ${isUser ? "user" : "bot"}`}>
        {!isUser && message.llmUsed === false && sources.length > 0 && (
          <div className="fallback-notice">{t.fallbackNotice}</div>
        )}
        {isUser ? (
          message.text
        ) : (
          <div className={`answer${message.streaming ? " streaming" : ""}`}>
            {renderAnswer(message.text, message.id, sources.length)}
          </div>
        )}

        {!isUser && sources.length > 0 && (
          <div className="sources">
            <div className="sources-label">{t.sourcesLabel}</div>
            {sources.map((s) => (
              <details className="source-item" key={s.id} id={`src-${message.id}-${s.n}`}>
                <summary>
                  <span className="src-n">{s.n}</span>
                  <span className={`badge ${s.category === "precedent" ? "precedent" : "law"}`}>
                    {s.category === "precedent" ? t.badgePrecedent : t.badgeLaw}
                  </span>
                  <span className="citation">{s.citation}</span>
                </summary>
                <div className="src-body">
                  <div className="title">{s.title}</div>
                  <div className="snippet">{s.snippet}…</div>
                  {s.url && (
                    <a className="src-link" href={s.url} target="_blank" rel="noopener noreferrer">
                      {t.officialSource} ↗
                    </a>
                  )}
                </div>
              </details>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
