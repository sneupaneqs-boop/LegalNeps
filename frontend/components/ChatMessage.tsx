import { Source } from "@/lib/api";
import { Lang, strings } from "@/lib/i18n";

export type Message = {
  role: "user" | "bot";
  text: string;
  sources?: Source[];
  llmUsed?: boolean;
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

  return (
    <div className={`bubble-row ${isUser ? "user" : "bot"}`}>
      <div className={`bubble ${isUser ? "user" : "bot"}`}>
        {!isUser && message.llmUsed === false && (
          <div className="fallback-notice">{t.fallbackNotice}</div>
        )}
        {message.text}

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="sources">
            <div className="sources-label">{t.sourcesLabel}</div>
            {message.sources.map((s) => (
              <div className="source-item" key={s.id}>
                <span className="title">{s.title}</span> —{" "}
                <span className="citation">{s.citation}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
