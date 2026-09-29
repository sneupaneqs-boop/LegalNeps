"use client";

import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { ErrorBox, errorText, formatDate, Loading, Provision } from "@/components/ui";
import {
  aiFillField,
  ApiError,
  createDraft,
  DraftAnswers,
  DraftVersion,
  getDraft,
  listDraftVersions,
  updateDraft,
} from "@/lib/api";
import {
  DraftField as DraftingField,
  DraftFormat,
  DraftTemplateDetail as DraftingTemplateDetail,
  draftUi,
  getTemplate,
  officialLine,
  renderDraftFile,
} from "@/lib/drafting";
import { saveBlob } from "@/lib/download";
import { useLang } from "@/lib/LangContext";
import { useAuth } from "@/lib/useAuth";
import "../draft.css";

export default function TemplatePage() {
  // useSearchParams needs a Suspense boundary for static rendering
  return (
    <Suspense
      fallback={
        <div className="page">
          <div className="content">
            <Loading />
          </div>
        </div>
      }
    >
      <TemplateForm />
    </Suspense>
  );
}

type Msg = { kind: "success" | "error" | "warn"; text: string } | null;

function TemplateForm() {
  const { templateId } = useParams<{ templateId: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();
  const draftParam = searchParams.get("draft");
  const { lang, t } = useLang();
  const ui = draftUi[lang];
  const { session, loading: authLoading } = useAuth();
  const token = session?.access_token;

  const [tpl, setTpl] = useState<DraftingTemplateDetail | null>(null);
  const [tplError, setTplError] = useState<{ e: unknown } | null>(null);
  const [answers, setAnswers] = useState<DraftAnswers>({});
  const [docLang, setDocLang] = useState<"en" | "ne">(lang);
  const [title, setTitle] = useState("");
  const [draftId, setDraftId] = useState<string | null>(draftParam);
  const [draftMissing, setDraftMissing] = useState(false);
  const [showErrors, setShowErrors] = useState(false);
  const [busy, setBusy] = useState<"" | "download" | "pdf" | "save">("");
  const [msg, setMsg] = useState<Msg>(null);
  const [aiBusy, setAiBusy] = useState<string | null>(null);
  const [aiMsg, setAiMsg] = useState<{ field: string; text: string; kind: "error" | "success" } | null>(null);
  const [undo, setUndo] = useState<Record<string, string>>({});
  const [versions, setVersions] = useState<DraftVersion[] | null>(null);
  const [versionsError, setVersionsError] = useState<{ e: unknown } | null>(null);
  const loadedDraft = useRef<string | null>(null);
  const langTouched = useRef(false);

  // the document language follows the UI language until the user picks one (or a draft sets it)
  useEffect(() => {
    if (!langTouched.current) setDocLang(lang);
  }, [lang]);

  // ---- template ----
  const loadTemplate = useCallback(() => {
    setTplError(null);
    setTpl(null);
    getTemplate(templateId)
      .then((d) => {
        setTpl(d);
        // preset select fields that have a default (e.g. "print the schedule heading: yes")
        const defaults: DraftAnswers = {};
        for (const f of d.fields) if (f.type === "select" && f.default != null) defaults[f.id] = String(f.default);
        setAnswers((prev) => ({ ...defaults, ...prev }));
        if (!d.languages.includes("en")) {
          langTouched.current = true;
          setDocLang("ne");
        }
      })
      .catch((e) => setTplError({ e }));
  }, [templateId]);
  useEffect(loadTemplate, [loadTemplate]);

  // ---- reopen a saved draft (?draft=id) ----
  useEffect(() => {
    if (!draftParam || !token || loadedDraft.current === draftParam) return;
    loadedDraft.current = draftParam;
    setDraftId(draftParam);
    getDraft(token, draftParam)
      .then((d) => {
        setAnswers(d.answers || {});
        langTouched.current = true;
        setDocLang(d.language);
        setTitle(d.title || "");
      })
      .catch((e) => {
        if (e instanceof ApiError && e.status === 404) setDraftMissing(true);
        else setMsg({ kind: "error", text: errorText(e, t) });
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [draftParam, token]);

  // ---- version history ----
  const fetchVersions = useCallback(
    (id: string) => {
      if (!token) return;
      setVersionsError(null);
      listDraftVersions(token, id)
        .then(setVersions)
        .catch((e) => setVersionsError({ e }));
    },
    [token]
  );
  const loadVersions = () => {
    if (draftId) fetchVersions(draftId);
  };

  function setAnswer(id: string, value: string) {
    setAnswers((prev) => ({ ...prev, [id]: value }));
  }

  function missingFields(): DraftingField[] {
    if (!tpl) return [];
    return tpl.fields.filter((f) => f.required && !(answers[f.id] ?? "").trim());
  }

  function cleanAnswers(): DraftAnswers {
    const out: DraftAnswers = {};
    for (const [k, v] of Object.entries(answers)) if (v !== "") out[k] = v;
    return out;
  }

  async function handleDownload(format: DraftFormat = "docx") {
    setMsg(null);
    if (missingFields().length > 0) {
      setShowErrors(true);
      setMsg({
        kind: "warn",
        text: `${t.draftMissing} ${missingFields().map((f) => f.label[lang]).join(", ")}`,
      });
      return;
    }
    setBusy(format === "pdf" ? "pdf" : "download");
    try {
      const blob = await renderDraftFile(templateId, cleanAnswers(), docLang, format);
      saveBlob(blob, `${templateId}.${format}`);
      setMsg({ kind: "success", text: t.draftDownloaded });
    } catch (e) {
      setMsg({ kind: "error", text: errorText(e, t) });
    } finally {
      setBusy("");
    }
  }

  async function handleSave() {
    if (!token) return;
    setMsg(null);
    setBusy("save");
    try {
      const payload = { template_id: templateId, language: docLang, answers: cleanAnswers(), title: title.trim() || null };
      let savedId = draftId;
      if (draftId) {
        await updateDraft(token, draftId, payload);
      } else {
        const created = await createDraft(token, payload);
        savedId = created.id;
        setDraftId(created.id);
        loadedDraft.current = created.id;
        router.replace(`/draft/${templateId}?draft=${created.id}`);
      }
      setMsg({ kind: "success", text: t.draftSaved });
      if (savedId && versions !== null) fetchVersions(savedId);
    } catch (e) {
      setMsg({ kind: "error", text: errorText(e, t) });
    } finally {
      setBusy("");
    }
  }

  async function handleAiHelp(field: DraftingField) {
    if (!token) return;
    const hint = (answers[field.id] ?? "").trim();
    setAiMsg(null);
    if (!hint) {
      setAiMsg({ field: field.id, kind: "error", text: t.draftAiNeedText });
      return;
    }
    const others: DraftAnswers = {};
    for (const [k, v] of Object.entries(answers)) if (k !== field.id && v.trim()) others[k] = v;
    setAiBusy(field.id);
    try {
      const text = await aiFillField(token, templateId, {
        field_id: field.id,
        hint,
        language: docLang,
        other_answers: others,
      });
      setUndo((u) => ({ ...u, [field.id]: answers[field.id] ?? "" }));
      setAnswer(field.id, text);
    } catch (e) {
      setAiMsg({ field: field.id, kind: "error", text: errorText(e, t) });
    } finally {
      setAiBusy(null);
    }
  }

  if (tplError) {
    const notFound = tplError.e instanceof ApiError && tplError.e.status === 404;
    return (
      <div className="page">
        <div className="content">
          <Link className="back-link" href="/draft">
            {t.draftBackToList}
          </Link>
          {notFound ? <div className="notice">{t.draftNotFound}</div> : <ErrorBox message={errorText(tplError.e, t)} onRetry={loadTemplate} />}
        </div>
      </div>
    );
  }

  if (!tpl) {
    return (
      <div className="page">
        <div className="content">
          <Loading />
        </div>
      </div>
    );
  }

  const missing = showErrors ? new Set(missingFields().map((f) => f.id)) : new Set<string>();

  return (
    <div className="page">
      <div className="content">
        <Link className="back-link" href="/draft">
          {t.draftBackToList}
        </Link>
        <h2>{tpl.title[lang]}</h2>
        <p className="lede">{tpl.description[lang]}</p>

        {tpl.kind === "official" && tpl.source ? (
          <section className="card draft-format" aria-label={ui.formatBoxTitle} data-testid="format-box">
            <span className="draft-badge official" data-testid="official-format">
              {officialLine(tpl.source, lang)}
            </span>
            {(tpl.source.relates_to || tpl.source.form_title) && (
              <p className="muted">
                {tpl.source.relates_to ? `(${tpl.source.relates_to} सँग सम्बन्धित) ` : ""}
                {tpl.source.form_title ?? ""}
              </p>
            )}
            {tpl.source.url && (
              <p>
                <a href={tpl.source.url} target="_blank" rel="noopener noreferrer">
                  {ui.openOfficial}
                  {tpl.source.page ? ` (${ui.page} ${tpl.source.page})` : ""}
                </a>
              </p>
            )}
          </section>
        ) : (
          <section className="card draft-format" aria-label={ui.formatBoxTitle} data-testid="format-box">
            <span className="draft-badge standard">{ui.standardFormatLong}</span>
            {tpl.source?.note && <p className="draft-note">{tpl.source.note[lang]}</p>}
          </section>
        )}

        <section className="card" aria-label={t.basedOn}>
          <h3>{t.basedOn}</h3>
          {tpl.provisions.length === 0 && <div className="muted">{t.draftNoProvisions}</div>}
          <div className="list">
            {tpl.provisions.map((p, i) => (
              <Provision key={`${p.slug}-${p.section}-${i}`} p={p} lang={lang} />
            ))}
          </div>
        </section>

        {draftMissing && <div className="notice warn">{t.draftNotFoundDraft}</div>}
        {draftParam && !authLoading && !session && <div className="notice">{t.draftMyDraftsSignIn}</div>}

        <form
          className="form"
          onSubmit={(e) => {
            e.preventDefault();
            handleDownload();
          }}
          noValidate
        >
          {tpl.languages.includes("en") ? (
            <div className="field">
              <label htmlFor="doc-lang">{t.draftLanguage}</label>
              <select id="doc-lang" className="select" value={docLang} onChange={(e) => {
                  langTouched.current = true;
                  setDocLang(e.target.value as "en" | "ne");
                }}>
                <option value="en">{t.draftLangEn}</option>
                <option value="ne">{t.draftLangNe}</option>
              </select>
            </div>
          ) : (
            <div className="notice" data-testid="nepali-only">{ui.nepaliOnly}</div>
          )}

          {tpl.fields.map((f) => {
            const value = answers[f.id] ?? "";
            const invalid = missing.has(f.id);
            const id = `f-${f.id}`;
            return (
              <div className="field" key={f.id}>
                <label htmlFor={id}>
                  {f.label[lang]}
                  {f.required ? (
                    <span className="req" aria-label={t.required}>
                      *
                    </span>
                  ) : (
                    <span className="muted"> ({t.optional})</span>
                  )}
                </label>
                {f.type === "select" ? (
                  <select
                    id={id}
                    className={`select${invalid ? " invalid" : ""}`}
                    value={value}
                    onChange={(e) => setAnswer(f.id, e.target.value)}
                    aria-required={f.required}
                    aria-invalid={invalid}
                  >
                    <option value="">{ui.choose}</option>
                    {(f.options ?? []).map((o) => (
                      <option key={o.value} value={o.value}>
                        {o.label[lang]}
                      </option>
                    ))}
                  </select>
                ) : f.type === "textarea" ? (
                  <textarea
                    id={id}
                    className={`textarea${invalid ? " invalid" : ""}`}
                    value={value}
                    onChange={(e) => setAnswer(f.id, e.target.value)}
                    aria-required={f.required}
                    aria-invalid={invalid}
                  />
                ) : (
                  <input
                    id={id}
                    className={`input${invalid ? " invalid" : ""}`}
                    type={f.type === "number" ? "number" : f.type === "date" ? "date" : "text"}
                    inputMode={f.type === "number" ? "decimal" : undefined}
                    value={value}
                    onChange={(e) => setAnswer(f.id, e.target.value)}
                    aria-required={f.required}
                    aria-invalid={invalid}
                  />
                )}
                {f.help && <div className="help">{f.help[lang]}</div>}
                {f.type === "textarea" && (
                  <div>
                    {session ? (
                      <div className="row">
                        <button
                          type="button"
                          className="btn btn-small"
                          disabled={aiBusy === f.id}
                          onClick={() => handleAiHelp(f)}
                        >
                          ✨ {aiBusy === f.id ? t.draftAiWorking : t.draftAiHelp}
                        </button>
                        {undo[f.id] !== undefined && (
                          <button
                            type="button"
                            className="btn btn-small"
                            onClick={() => {
                              setAnswer(f.id, undo[f.id]);
                              setUndo((u) => {
                                const n = { ...u };
                                delete n[f.id];
                                return n;
                              });
                            }}
                          >
                            ↩
                          </button>
                        )}
                        <span className="help">{t.draftAiHint}</span>
                      </div>
                    ) : (
                      !authLoading && <div className="help">{t.draftAiSignIn}</div>
                    )}
                    {undo[f.id] !== undefined && <div className="help">{t.draftAiDisclaimer}</div>}
                    {aiMsg && aiMsg.field === f.id && (
                      <div className={`notice ${aiMsg.kind}`} role="alert" style={{ marginTop: 6 }}>
                        {aiMsg.text}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}

          {session && (
            <div className="field">
              <label htmlFor="draft-title">{t.draftTitleLabel}</label>
              <input id="draft-title" className="input" value={title} maxLength={200} onChange={(e) => setTitle(e.target.value)} />
            </div>
          )}

          {tpl.formats.includes("pdf") && <div className="draft-note">{ui.pdfNote}</div>}

          {msg && (
            <div className={`notice ${msg.kind}`} role={msg.kind === "error" ? "alert" : "status"}>
              {msg.text}
            </div>
          )}

          <div className="row">
            <button type="submit" className="btn btn-primary" disabled={busy !== ""} data-testid="download-docx">
              {busy === "download" ? ui.downloading : ui.downloadDocx}
            </button>
            {tpl.formats.includes("pdf") && (
              <button
                type="button"
                className="btn btn-primary"
                disabled={busy !== ""}
                onClick={() => handleDownload("pdf")}
                data-testid="download-pdf"
              >
                {busy === "pdf" ? ui.downloading : ui.downloadPdf}
              </button>
            )}
            {session ? (
              <button type="button" className="btn" disabled={busy !== ""} onClick={handleSave}>
                {busy === "save" ? t.saving : draftId ? t.draftUpdateDraft : t.draftSaveDraft}
              </button>
            ) : (
              !authLoading && <span className="muted">{t.draftMyDraftsSignIn}</span>
            )}
          </div>
        </form>

        {session && draftId && (
          <details
            className="card"
            onToggle={(e) => {
              if ((e.currentTarget as HTMLDetailsElement).open && versions === null) loadVersions();
            }}
          >
            <summary style={{ cursor: "pointer", fontWeight: 600 }}>{t.draftVersions}</summary>
            <div style={{ marginTop: 10 }}>
              {versionsError && <ErrorBox message={errorText(versionsError.e, t)} onRetry={loadVersions} />}
              {!versionsError && versions === null && <Loading />}
              {versions && versions.length === 0 && <div className="muted">{t.draftNoVersions}</div>}
              {versions && versions.length > 0 && (
                <ul className="list">
                  {[...versions]
                    .sort((a, b) => b.version_number - a.version_number)
                    .map((v) => (
                      <li className="list-item" key={v.id}>
                        <div className="grow">
                          <strong>
                            {t.draftVersionN} {v.version_number}
                          </strong>{" "}
                          <span className="muted">
                            · {formatDate(v.created_at, lang)} · {v.language === "ne" ? t.draftLangNe : t.draftLangEn}
                          </span>
                        </div>
                        <button
                          type="button"
                          className="btn btn-small"
                          onClick={() => {
                            setAnswers(v.answers || {});
                            setDocLang(v.language);
                            setMsg({ kind: "success", text: t.draftRestored });
                            window.scrollTo({ top: 0, behavior: "smooth" });
                          }}
                        >
                          {t.draftRestore}
                        </button>
                      </li>
                    ))}
                </ul>
              )}
            </div>
          </details>
        )}
      </div>
    </div>
  );
}
