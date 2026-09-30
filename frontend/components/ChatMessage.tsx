import Link from "next/link";
import { PlaybookCard, Source, Verification } from "@/lib/api";
import { Lang, strings } from "@/lib/i18n";
import { renderAnswer } from "@/lib/markdown";
import "./chat-extras.css";

export type Message = {
  id: string;
  role: "user" | "bot";
  text: string;
  sources?: Source[];
  llmUsed?: boolean;
  streaming?: boolean;
  question?: string;
  saved?: boolean;
  saving?: boolean;
  playbook?: PlaybookCard | null;
  verification?: Verification | null;
};

const x = {
  en: {
    plan: "Action plan",
    openPlan: "Open the full step-by-step plan",
    where: "Where to go",
    sharper: "For a sharper answer, tell me:",
    evidence: "Evidence check",
    supported: (s: number, n: number) => `${s} of ${n} legal claims are backed by the cited official sources`,
    counts: (l: number, p: number) => `${l} law ${l === 1 ? "section" : "sections"} · ${p} ${p === 1 ? "precedent" : "precedents"} cited`,
    unverified: (n: number) =>
      `${n} ${n === 1 ? "claim" : "claims"} could not be matched to a source and ${n === 1 ? "is" : "are"} marked ⚠ — confirm with an advocate before relying on ${n === 1 ? "it" : "them"}.`,
    removed: (n: number) =>
      `${n} ${n === 1 ? "statement was" : "statements were"} removed because ${n === 1 ? "it" : "they"} couldn't be verified against the sources.`,
    checking: "Checking sources…",
    status: {
      in_force: "In force", bill: "Bill — not law", repealed: "Repealed", lapsed: "Lapsed ordinance",
      ordinance: "Ordinance — temporary", unknown: "Status unverified",
    } as Record<string, string>,
    core: "Core law",
    older: (y?: number | null) => `Older law${y ? ` · BS ${y}` : ""}`,
    olderTip: "Decided before the law that now governs this topic — historical context, not the current rule.",
  },
  ne: {
    plan: "कार्ययोजना",
    openPlan: "पूरा चरणबद्ध योजना हेर्नुहोस्",
    where: "कहाँ जाने",
    sharper: "अझ सटीक जवाफका लागि भन्नुहोस्:",
    evidence: "प्रमाण जाँच",
    supported: (s: number, n: number) => `${n} मध्ये ${s} कानुनी भनाइ उद्धृत आधिकारिक स्रोतले पुष्टि गर्छ`,
    counts: (l: number, p: number) => `${l} कानुनी दफा · ${p} नजिर उद्धृत`,
    unverified: (n: number) => `${n} भनाइ स्रोतसँग मिलाउन सकिएन र ⚠ चिन्ह लगाइएको छ — भर पर्नुअघि अधिवक्तासँग पुष्टि गर्नुहोस्।`,
    removed: (n: number) => `${n} भनाइ स्रोतसँग पुष्टि गर्न नसकिएकाले हटाइयो।`,
    checking: "स्रोतसँग जाँच गर्दै…",
    status: {
      in_force: "लागू", bill: "विधेयक — कानुन होइन", repealed: "खारेज", lapsed: "निष्क्रिय अध्यादेश",
      ordinance: "अध्यादेश — अस्थायी", unknown: "स्थिति अपुष्ट",
    } as Record<string, string>,
    core: "मुख्य कानुन",
    older: (y?: number | null) => `पुरानो कानुन${y ? ` · वि.सं. ${y}` : ""}`,
    olderTip: "यो विषय अहिले नियन्त्रण गर्ने कानुन आउनुअघिको निर्णय — ऐतिहासिक सन्दर्भ मात्र, हालको नियम होइन।",
  },
};

function statusClass(status?: string | null) {
  if (status === "in_force") return "ok";
  if (status === "bill" || status === "repealed" || status === "lapsed") return "bad";
  return "warn";
}

export default function ChatMessage({
  message,
  lang,
  canSave,
  onSave,
  onPrefill,
}: {
  message: Message;
  lang: Lang;
  canSave?: boolean;
  onSave?: (m: Message) => void;
  onPrefill?: (text: string) => void;
}) {
  const t = strings[lang];
  const e = x[lang];
  const isUser = message.role === "user";
  const sources = message.sources ?? [];
  const showSave = !isUser && !message.streaming && message.text && message.question && onSave;
  const pb = message.playbook;
  const v = message.verification;
  const unverified = v?.unverified?.length ?? 0;
  const removedN = v?.removed?.count ?? 0;

  return (
    <div className={`bubble-row ${isUser ? "user" : "bot"}`}>
      <div className={`bubble ${isUser ? "user" : "bot"}`}>
        {!isUser && pb && (
          <div className="plan-card">
            <div className="plan-kicker">{e.plan}</div>
            <div className="plan-title">{pb.issue[lang] || pb.issue.en}</div>
            {pb.forum && (
              <div className="plan-forum">
                <strong>{e.where}:</strong> {pb.forum[lang] || pb.forum.en}
              </div>
            )}
            <Link className="plan-link" href={`/action-plans/${pb.id}`}>
              {e.openPlan} →
            </Link>
            {pb.fact_questions?.length > 0 && !message.streaming && (
              <div className="fact-chips">
                <div className="fact-label">{e.sharper}</div>
                {pb.fact_questions.slice(0, 4).map((q) => {
                  const label = q[lang] || q.en;
                  return (
                    <button key={label} className="fact-chip" onClick={() => onPrefill?.(`${label} → `)}>
                      {label}
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {!isUser && message.llmUsed === false && sources.length > 0 && (
          <div className="fallback-notice">{t.fallbackNotice}</div>
        )}
        {isUser ? (
          message.text
        ) : (
          <div className={`answer${message.streaming ? " streaming" : ""}`}>
            {message.streaming && !message.text ? (
              <div className="checking">{e.checking}</div>
            ) : (
              renderAnswer(message.text, message.id, sources.length)
            )}
          </div>
        )}

        {!isUser && !message.streaming && v && v.claims > 0 && (
          <div className={`evidence ${unverified ? "has-gaps" : "all-ok"}`}>
            <div className="evidence-title">
              {unverified ? "⚠" : "✓"} {e.evidence}
            </div>
            <div>{e.supported(v.supported, v.claims)}</div>
            <div className="evidence-sub">{e.counts(v.cited_laws, v.cited_precedents)}</div>
            {unverified > 0 && <div className="evidence-warn">{e.unverified(unverified)}</div>}
            {removedN > 0 && <div className="evidence-removed">{e.removed(removedN)}</div>}
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
                  {s.pinned && <span className="badge core">{e.core}</span>}
                  {s.category === "precedent" && s.stale && (
                    <span className="badge status warn" title={e.olderTip}>
                      {e.older(s.decided_bs)}
                    </span>
                  )}
                  {s.category !== "precedent" && s.status && s.status !== "in_force" && (
                    <span className={`badge status ${statusClass(s.status)}`}>{e.status[s.status] ?? s.status}</span>
                  )}
                  {s.category !== "precedent" && s.status === "in_force" && (
                    <span className="badge status ok">{e.status.in_force}</span>
                  )}
                  <span className="citation">{s.citation}</span>
                </summary>
                <div className="src-body">
                  <div className="title">{s.title}</div>
                  {s.stale && <div className="src-note">{e.olderTip}</div>}
                  <div className="snippet">{s.snippet}…</div>
                  {s.slug && s.section && (
                    <Link className="src-link" href={`/law/${s.slug}/${encodeURIComponent(s.section)}`}>
                      {lang === "ne" ? "पूरा दफा पढ्नुहोस्" : "Read the full section"} →
                    </Link>
                  )}{" "}
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

        {showSave && (
          <div className="save-row">
            {message.saved ? (
              <span className="saved-badge">✓ {t.savedResearch}</span>
            ) : (
              <button
                className="save-button"
                disabled={!canSave || message.saving}
                title={canSave ? undefined : t.signInToSave}
                onClick={() => onSave!(message)}
              >
                {message.saving ? "…" : t.saveResearch}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
