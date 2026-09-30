"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  AuditResult,
  auditDocument,
  ChecklistType,
  CONTRACT_TYPE_LABELS,
  CONTRACT_TYPES,
  ContractType,
  DocumentsApiError,
  downloadAuditReport,
  Finding,
  FindingStatus,
  getChecklists,
  listMatters,
  MatterSummary,
  STATUS_ORDER,
} from "@/lib/documents";
import { Lang } from "@/lib/i18n";
import { useLang } from "@/lib/LangContext";
import { authAvailable } from "@/lib/supabase";
import { useAuth } from "@/lib/useAuth";
import "./audit.css";

const MAX_BYTES = 20 * 1024 * 1024;

// Page copy lives here (not lib/i18n.ts) so this feature is self-contained.
const L = {
  en: {
    title: "Contract audit",
    subtitle: "Upload a contract and get an audit checked against cited Nepali law.",
    notice: "Legal information, not legal advice — have an advocate review the contract before you sign it.",
    howTitle: "How it works",
    how: "An AI reader only extracts what the contract says. The judgement — is 8 months of probation allowed? — is made by fixed rules that cite the Labour Act or the Civil Code, so every finding links to the exact section.",
    signInTitle: "Sign in to audit a contract",
    signInBody: "Use the Sign in button at the top of the page. Your audits count towards your daily limit.",
    authOff: "Sign-in isn't configured on this site, so the audit can't be used here.",
    fileLabel: "Contract file (PDF or DOCX, up to 20 MB)",
    fileDrop: "Choose a file or drop it here",
    fileHint: "Use a Unicode PDF or DOCX. Scanned images and old Nepali fonts (Preeti) can't be read.",
    remove: "Remove",
    typeLabel: "Contract type",
    typeAuto: "Auto-detect",
    matterLabel: "Save a copy to a matter (optional)",
    matterNone: "Don't save the document",
    consent:
      "I consent to this document being processed to produce the audit; it isn't stored unless I save it to a matter.",
    run: "Audit contract",
    running: "Reading and checking your contract… this can take up to a minute.",
    whatWeCheck: "What we check",
    notEnforced: "Considered but not enforced (the number couldn't be confirmed in the law text)",
    resultsTitle: "Audit result",
    detectedAs: "Detected as",
    setBy: "Chosen by you",
    byKeywords: "auto-detected",
    byLlm: "auto-detected",
    clauses: "clauses read",
    truncated: "The contract was long, so only its first part was analysed.",
    download: "Download DOCX report",
    downloading: "Preparing…",
    another: "Audit another contract",
    colFinding: "Finding",
    colWhere: "In the contract",
    colTodo: "What to do",
    colBasis: "Legal basis",
    notStated: "Not stated in the contract",
    okNote: "Not stated in the contract — the statutory rule applies by default.",
    foundLabel: "Found",
    statutory: "Required or limited by law",
    bestPractice: "Best practice — the law leaves this to the parties",
    officialPdf: "official text",
    noFindings: "Nothing in this group.",
    savedToMatter: "A copy was saved to the matter you chose.",
    status: {
      issue: "Issues",
      warning: "Warnings",
      missing: "Missing",
      info: "Suggestions",
      ok: "Looks fine",
    } as Record<FindingStatus, string>,
    statusOne: {
      issue: "Issue",
      warning: "Warning",
      missing: "Missing",
      info: "Suggestion",
      ok: "OK",
    } as Record<FindingStatus, string>,
    errTooBig: "That file is over 20 MB.",
    errType: "Please choose a PDF or DOCX file.",
    errAuth: "Please sign in again and retry.",
    errQuota: "You've reached today's limit. Try again tomorrow, or upgrade your plan.",
    errBig: "That file is too large (20 MB limit).",
    errGeneric: "Something went wrong. Please try again.",
    errDownload: "Couldn't prepare the report. Please try again.",
  },
  ne: {
    title: "सम्झौता परीक्षण",
    subtitle: "सम्झौता अपलोड गर्नुहोस् र नेपाल कानूनका दफासहित परीक्षण प्राप्त गर्नुहोस्।",
    notice:
      "यो कानूनी जानकारी हो, कानूनी सल्लाह होइन — हस्ताक्षर गर्नुअघि अधिवक्ताबाट सम्झौता समीक्षा गराउनुहोस्।",
    howTitle: "यो कसरी काम गर्छ",
    how: "एआई पाठकले सम्झौतामा के लेखिएको छ त्यही मात्र निकाल्छ। ८ महिनाको परीक्षणकाल मिल्छ कि मिल्दैन भन्ने निर्णय श्रम ऐन वा देवानी संहिताको दफा उद्धृत गर्ने निश्चित नियमहरूले गर्छन्, त्यसैले हरेक नतिजा ठ्याक्कै दफासँग जोडिएको हुन्छ।",
    signInTitle: "सम्झौता परीक्षण गर्न साइन इन गर्नुहोस्",
    signInBody: "पृष्ठको माथिको साइन इन बटन प्रयोग गर्नुहोस्। तपाईंका परीक्षण दैनिक सीमामा गनिन्छन्।",
    authOff: "यो साइटमा साइन इन सेटअप गरिएको छैन, त्यसैले परीक्षण प्रयोग गर्न मिल्दैन।",
    fileLabel: "सम्झौताको फाइल (PDF वा DOCX, २० MB सम्म)",
    fileDrop: "फाइल छान्नुहोस् वा यहाँ राख्नुहोस्",
    fileHint: "युनिकोड PDF वा DOCX प्रयोग गर्नुहोस्। स्क्यान गरिएको तस्बिर र पुरानो नेपाली फन्ट (प्रीति) पढ्न सकिँदैन।",
    remove: "हटाउनुहोस्",
    typeLabel: "सम्झौताको प्रकार",
    typeAuto: "स्वतः पहिचान",
    matterLabel: "केस फाइलमा प्रति सुरक्षित गर्नुहोस् (ऐच्छिक)",
    matterNone: "कागजात सुरक्षित नगर्नुहोस्",
    consent:
      "म यो कागजात परीक्षण तयार गर्न प्रशोधन गरिनेमा सहमत छु; म यसलाई केस फाइलमा सुरक्षित नगरेसम्म यो भण्डारण गरिँदैन।",
    run: "सम्झौता परीक्षण गर्नुहोस्",
    running: "तपाईंको सम्झौता पढ्दै र जाँच्दै… यसमा एक मिनेटसम्म लाग्न सक्छ।",
    whatWeCheck: "हामीले के जाँच्छौं",
    notEnforced: "विचार गरिएका तर लागू नगरिएका (कानूनको पाठमा सङ्ख्या पुष्टि हुन सकेन)",
    resultsTitle: "परीक्षणको नतिजा",
    detectedAs: "पहिचान",
    setBy: "तपाईंले छानेको",
    byKeywords: "स्वतः पहिचान",
    byLlm: "स्वतः पहिचान",
    clauses: "दफा/बुँदा पढियो",
    truncated: "सम्झौता लामो भएकाले सुरुको भाग मात्र विश्लेषण गरियो।",
    download: "DOCX प्रतिवेदन डाउनलोड",
    downloading: "तयार गर्दै…",
    another: "अर्को सम्झौता परीक्षण गर्नुहोस्",
    colFinding: "नतिजा",
    colWhere: "सम्झौतामा",
    colTodo: "के गर्ने",
    colBasis: "कानूनी आधार",
    notStated: "सम्झौतामा उल्लेख छैन",
    okNote: "सम्झौतामा उल्लेख छैन — कानूनको व्यवस्था स्वतः लागू हुन्छ।",
    foundLabel: "भेटिएको",
    statutory: "कानूनले तोकेको वा सीमित गरेको",
    bestPractice: "उत्तम अभ्यास — कानूनले पक्षहरूमै छाडेको",
    officialPdf: "आधिकारिक पाठ",
    noFindings: "यो समूहमा केही छैन।",
    savedToMatter: "तपाईंले छानेको केस फाइलमा प्रति सुरक्षित गरियो।",
    status: {
      issue: "समस्या",
      warning: "चेतावनी",
      missing: "नभएको",
      info: "सुझाव",
      ok: "ठीक देखिन्छ",
    } as Record<FindingStatus, string>,
    statusOne: {
      issue: "समस्या",
      warning: "चेतावनी",
      missing: "नभएको",
      info: "सुझाव",
      ok: "ठीक",
    } as Record<FindingStatus, string>,
    errTooBig: "त्यो फाइल २० MB भन्दा ठूलो छ।",
    errType: "कृपया PDF वा DOCX फाइल छान्नुहोस्।",
    errAuth: "कृपया फेरि साइन इन गरी पुनः प्रयास गर्नुहोस्।",
    errQuota: "तपाईंले आजको सीमा पुर्‍याउनुभयो। भोलि फेरि प्रयास गर्नुहोस् वा योजना अपग्रेड गर्नुहोस्।",
    errBig: "त्यो फाइल धेरै ठूलो छ (२० MB सीमा)।",
    errGeneric: "केही गडबड भयो। कृपया फेरि प्रयास गर्नुहोस्।",
    errDownload: "प्रतिवेदन तयार गर्न सकिएन। कृपया फेरि प्रयास गर्नुहोस्।",
  },
};

function humanize(name: string): string {
  return name.replace(/_/g, " ");
}

function fmtValue(v: number | string | boolean): string {
  if (typeof v === "number") return Number.isInteger(v) ? v.toLocaleString("en-US") : String(v);
  return String(v);
}

function fmtBytes(n: number): string {
  return n >= 1024 * 1024 ? `${(n / (1024 * 1024)).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`;
}

export default function AuditPage() {
  // shared with the app shell's language toggle (the page used to keep its own copy and header)
  const { lang } = useLang();
  const p = L[lang];
  const { session, loading: authLoading } = useAuth();

  const [file, setFile] = useState<File | null>(null);
  const [contractType, setContractType] = useState<ContractType | "auto">("auto");
  const [consent, setConsent] = useState(false);
  const [matters, setMatters] = useState<MatterSummary[]>([]);
  const [matterId, setMatterId] = useState("");
  const [checklists, setChecklists] = useState<ChecklistType[] | null>(null);

  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<AuditResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    getChecklists()
      .then(setChecklists)
      .catch(() => setChecklists(null));
  }, []);

  useEffect(() => {
    if (!session) {
      setMatters([]);
      setMatterId("");
      return;
    }
    listMatters(session.access_token)
      .then(setMatters)
      .catch(() => setMatters([]));
  }, [session]);

  function pickFile(f: File | null) {
    setError(null);
    if (!f) return;
    const name = f.name.toLowerCase();
    if (!name.endsWith(".pdf") && !name.endsWith(".docx")) {
      setError(p.errType);
      return;
    }
    if (f.size > MAX_BYTES) {
      setError(p.errTooBig);
      return;
    }
    setFile(f);
  }

  function describe(e: unknown): string {
    if (e instanceof DocumentsApiError) {
      if (e.status === 401) return p.errAuth;
      if (e.status === 429) return p.errQuota;
      if (e.status === 413) return p.errBig;
      if (lang === "ne" && e.messageNe) return e.messageNe;
      if (e.code) return e.message; // server-written, user-safe (legacy font, scanned PDF, ...)
    }
    return p.errGeneric;
  }

  async function runAudit(ev: React.FormEvent) {
    ev.preventDefault();
    if (!session || !file || !consent || running) return;
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const res = await auditDocument(session.access_token, file, {
        contractType,
        language: lang,
        matterId: matterId || undefined,
      });
      setResult(res);
    } catch (e) {
      setError(describe(e));
    } finally {
      setRunning(false);
    }
  }

  async function handleDownload() {
    if (!session || !result) return;
    setDownloading(true);
    setError(null);
    try {
      const blob = await downloadAuditReport(session.access_token, result, lang);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "contract-audit.docx";
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 2000);
    } catch {
      setError(p.errDownload);
    } finally {
      setDownloading(false);
    }
  }

  function reset() {
    setResult(null);
    setFile(null);
    setError(null);
    setConsent(false);
    if (inputRef.current) inputRef.current.value = "";
  }

  const grouped = useMemo(() => {
    const g: Record<FindingStatus, Finding[]> = { issue: [], warning: [], missing: [], info: [], ok: [] };
    for (const f of result?.findings ?? []) g[f.status].push(f);
    return g;
  }, [result]);

  const visibleChecklists = useMemo(() => {
    if (!checklists) return [];
    return contractType === "auto" ? checklists : checklists.filter((c) => c.contract_type === contractType);
  }, [checklists, contractType]);

  const signedIn = !!session;

  return (
    <div className="page au-page">
      <main className="au-body">
        <section className="au-hero">
          <h2>{p.title}</h2>
          <p>{p.subtitle}</p>
        </section>

        <div className="au-notice" role="note">
          {p.notice}
        </div>

        {authLoading && <div className="au-muted">…</div>}

        {!authLoading && !signedIn && (
          <section className="au-card au-signin">
            <h3>{p.signInTitle}</h3>
            <p>{authAvailable() ? p.signInBody : p.authOff}</p>
          </section>
        )}

        {!authLoading && signedIn && !result && (
          <form className="au-card au-form" onSubmit={runAudit}>
            <div className="au-field">
              <span className="au-label" id="au-file-label">
                {p.fileLabel}
              </span>
              <label
                className={`au-drop${dragging ? " au-drop-active" : ""}${file ? " au-drop-has" : ""}`}
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragging(true);
                }}
                onDragLeave={() => setDragging(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setDragging(false);
                  pickFile(e.dataTransfer.files?.[0] ?? null);
                }}
              >
                <input
                  ref={inputRef}
                  type="file"
                  accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                  aria-labelledby="au-file-label"
                  onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
                />
                {file ? (
                  <span className="au-file">
                    <strong>{file.name}</strong> <span className="au-muted">({fmtBytes(file.size)})</span>
                  </span>
                ) : (
                  <span>{p.fileDrop}</span>
                )}
              </label>
              {file && (
                <button
                  type="button"
                  className="au-link-button"
                  onClick={() => {
                    setFile(null);
                    if (inputRef.current) inputRef.current.value = "";
                  }}
                >
                  {p.remove}
                </button>
              )}
              <span className="au-hint">{p.fileHint}</span>
            </div>

            <div className="au-field">
              <label className="au-label" htmlFor="au-type">
                {p.typeLabel}
              </label>
              <select
                id="au-type"
                value={contractType}
                onChange={(e) => setContractType(e.target.value as ContractType | "auto")}
              >
                <option value="auto">{p.typeAuto}</option>
                {CONTRACT_TYPES.map((c) => (
                  <option key={c} value={c}>
                    {CONTRACT_TYPE_LABELS[c][lang]}
                  </option>
                ))}
              </select>
            </div>

            {matters.length > 0 && (
              <div className="au-field">
                <label className="au-label" htmlFor="au-matter">
                  {p.matterLabel}
                </label>
                <select id="au-matter" value={matterId} onChange={(e) => setMatterId(e.target.value)}>
                  <option value="">{p.matterNone}</option>
                  {matters.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.client_name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <label className="au-consent">
              <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
              <span>{p.consent}</span>
            </label>

            {error && (
              <div className="au-error" role="alert">
                {error}
              </div>
            )}

            <button className="au-primary" type="submit" disabled={!file || !consent || running}>
              {running ? p.running : p.run}
            </button>
            {running && <div className="au-progress" aria-hidden="true" />}
          </form>
        )}

        {!authLoading && signedIn && !result && visibleChecklists.length > 0 && (
          <details className="au-card au-checks">
            <summary>{p.whatWeCheck}</summary>
            {visibleChecklists.map((c) => (
              <div className="au-check-type" key={c.contract_type}>
                <h4>{c.title[lang]}</h4>
                <ul>
                  {c.checks.map((k) => (
                    <li key={k.id}>
                      {k.title[lang]}{" "}
                      <Link className="au-cite" href={`/law/${k.provision.slug}/${encodeURIComponent(k.provision.section)}`}>
                        {lang === "ne" ? k.provision.citation : k.provision.citation_en}
                      </Link>
                    </li>
                  ))}
                </ul>
                {c.not_enforced.length > 0 && (
                  <>
                    <div className="au-muted au-small">{p.notEnforced}</div>
                    <ul className="au-muted au-small">
                      {c.not_enforced.map((n) => (
                        <li key={n.id}>{n.title[lang]}</li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            ))}
          </details>
        )}

        {result && (
          <section className="au-results" aria-live="polite">
            <div className="au-card au-summary">
              <h3>{p.resultsTitle}</h3>
              <p className="au-meta">
                {result.filename && <strong>{result.filename}</strong>}
                {result.filename && " · "}
                {result.detected_by === "user" ? p.setBy : p.detectedAs}: {result.contract_type_title[lang]} ·{" "}
                {result.clause_count} {p.clauses}
              </p>
              {result.truncated && <p className="au-warn-text">{p.truncated}</p>}
              {result.saved_to_matter && <p className="au-muted">{p.savedToMatter}</p>}
              <div className="au-chips">
                {STATUS_ORDER.map((s) => (
                  <span key={s} className={`au-chip au-chip-${s}`}>
                    {p.status[s]}: {result.summary[s] ?? 0}
                  </span>
                ))}
              </div>
              <div className="au-actions">
                <button className="au-primary" onClick={handleDownload} disabled={downloading}>
                  {downloading ? p.downloading : p.download}
                </button>
                <button className="au-secondary" onClick={reset}>
                  {p.another}
                </button>
              </div>
              {error && (
                <div className="au-error" role="alert">
                  {error}
                </div>
              )}
            </div>

            {STATUS_ORDER.map((s) => {
              const rows = grouped[s];
              if (rows.length === 0) return null;
              const table = (
                <table className="au-table">
                  <thead>
                    <tr>
                      <th>{p.colFinding}</th>
                      <th>{p.colWhere}</th>
                      <th>{p.colTodo}</th>
                      <th>{p.colBasis}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((f) => (
                      <FindingRow key={f.check_id} f={f} lang={lang} />
                    ))}
                  </tbody>
                </table>
              );
              return (
                <section key={s} className={`au-group au-group-${s}`}>
                  {s === "ok" ? (
                    <details>
                      <summary>
                        {p.status[s]} ({rows.length})
                      </summary>
                      {table}
                    </details>
                  ) : (
                    <>
                      <h3>
                        {p.status[s]} ({rows.length})
                      </h3>
                      {table}
                    </>
                  )}
                </section>
              );
            })}
          </section>
        )}

        <div className="au-notice au-notice-foot" role="note">
          {p.notice}
        </div>
        <p className="au-muted au-small au-how">
          <strong>{p.howTitle}.</strong> {p.how}
        </p>
      </main>
    </div>
  );
}

function FindingRow({ f, lang }: { f: Finding; lang: Lang }) {
  const p = L[lang];
  const facts = Object.entries(f.facts).filter(([, v]) => typeof v !== "boolean");
  const prov = f.provision;
  return (
    <tr className={`au-row au-row-${f.status}`}>
      <td data-label={p.colFinding}>
        <span className={`au-badge au-badge-${f.status}`}>{p.statusOne[f.status]}</span>
        <div className="au-title">{f.title[lang]}</div>
        {facts.length > 0 && (
          <div className="au-facts">
            {p.foundLabel}: {facts.map(([k, v]) => `${humanize(k)} = ${fmtValue(v)}`).join("; ")}
          </div>
        )}
      </td>
      <td data-label={p.colWhere}>
        {f.clause_label ? (
          <>
            <div className="au-clause">{f.clause_label}</div>
            {f.quote && <blockquote>{f.quote}</blockquote>}
          </>
        ) : (
          <span className="au-muted">{f.status === "ok" ? p.okNote : p.notStated}</span>
        )}
      </td>
      <td data-label={p.colTodo}>{f.status === "ok" ? <span className="au-muted">—</span> : f.recommendation[lang]}</td>
      <td data-label={p.colBasis}>
        <Link className="au-cite" href={`/law/${prov.slug}/${encodeURIComponent(prov.section)}`}>
          {lang === "ne" ? prov.citation : prov.citation_en || prov.citation}
        </Link>
        {prov.url && (
          <>
            {" "}
            <a className="au-ext" href={prov.url} target="_blank" rel="noopener noreferrer">
              {p.officialPdf} ↗
            </a>
          </>
        )}
        <div className="au-basis">{f.basis === "statutory" ? p.statutory : p.bestPractice}</div>
      </td>
    </tr>
  );
}
