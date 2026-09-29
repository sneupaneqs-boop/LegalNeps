"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ErrorBox, errorText, formatDate, Loading } from "@/components/ui";
import { deleteDraft, DraftingTemplateSummary, listDraftingTemplates, listDrafts, SavedDraft } from "@/lib/api";
import { useLang } from "@/lib/LangContext";
import { useAuth } from "@/lib/useAuth";

export default function DraftPage() {
  const { lang, t } = useLang();
  const { session, loading: authLoading } = useAuth();
  const token = session?.access_token;

  const [templates, setTemplates] = useState<DraftingTemplateSummary[] | null>(null);
  const [tplError, setTplError] = useState<{ e: unknown } | null>(null);
  const [drafts, setDrafts] = useState<SavedDraft[] | null>(null);
  const [draftError, setDraftError] = useState<{ e: unknown } | null>(null);

  const loadTemplates = useCallback(() => {
    setTplError(null);
    setTemplates(null);
    listDraftingTemplates()
      .then(setTemplates)
      .catch((e) => setTplError({ e }));
  }, []);

  useEffect(loadTemplates, [loadTemplates]);

  const loadDrafts = useCallback(() => {
    if (!token) {
      setDrafts(null);
      return;
    }
    setDraftError(null);
    listDrafts(token)
      .then(setDrafts)
      .catch((e) => setDraftError({ e }));
  }, [token]);

  useEffect(loadDrafts, [loadDrafts]);

  async function handleDelete(d: SavedDraft) {
    if (!token || !window.confirm(t.confirmDelete)) return;
    try {
      await deleteDraft(token, d.id);
      setDrafts((prev) => prev?.filter((x) => x.id !== d.id) ?? null);
    } catch (e) {
      setDraftError({ e });
    }
  }

  const titleOf = (id: string) => templates?.find((x) => x.id === id)?.title[lang] ?? id;

  return (
    <div className="page">
      <div className="content">
        <h2>{t.draftTitle}</h2>
        <p className="lede">{t.draftIntro}</p>

        {tplError && <ErrorBox message={errorText(tplError.e, t)} onRetry={loadTemplates} />}
        {!tplError && templates === null && <Loading />}
        {templates && templates.length === 0 && <div className="notice">{t.draftNoTemplates}</div>}
        {templates && templates.length > 0 && (
          <section aria-label={t.draftTemplatesHeading}>
            <div className="card-grid" data-testid="template-list">
              {templates.map((tpl) => (
                <Link key={tpl.id} className="card card-link" href={`/draft/${tpl.id}`}>
                  <div className="card-title">{tpl.title[lang]}</div>
                  <div className="card-sub">{tpl.description[lang]}</div>
                </Link>
              ))}
            </div>
          </section>
        )}

        <section>
          <h3>{t.draftMyDrafts}</h3>
          {!authLoading && !session && <div className="notice">{t.draftMyDraftsSignIn}</div>}
          {session && draftError && <ErrorBox message={errorText(draftError.e, t)} onRetry={loadDrafts} />}
          {session && !draftError && drafts === null && <Loading />}
          {drafts && drafts.length === 0 && <div className="muted">{t.draftNoSaved}</div>}
          {drafts && drafts.length > 0 && (
            <ul className="list">
              {drafts.map((d) => (
                <li className="list-item" key={d.id}>
                  <div className="grow">
                    <div className="card-title">{d.title || titleOf(d.template_id)}</div>
                    <div className="muted">
                      {titleOf(d.template_id)} · {t.draftUpdated} {formatDate(d.updated_at, lang)}
                    </div>
                  </div>
                  <div className="row">
                    <Link className="btn btn-small" href={`/draft/${d.template_id}?draft=${d.id}`}>
                      {t.draftReopen}
                    </Link>
                    <button className="btn btn-small btn-danger" onClick={() => handleDelete(d)}>
                      {t.remove}
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
