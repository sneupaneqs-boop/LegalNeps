"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import AuthWidget from "@/components/AuthWidget";
import { deleteSavedResearch, listSavedResearch, SavedResearch } from "@/lib/api";
import { Lang, strings } from "@/lib/i18n";
import { useAuth } from "@/lib/useAuth";

export default function SavedPage() {
  const [lang, setLang] = useState<Lang>("en");
  const { session, loading: authLoading } = useAuth();
  const [items, setItems] = useState<SavedResearch[] | null>(null);
  const [error, setError] = useState(false);

  const t = strings[lang];

  useEffect(() => {
    if (!session) {
      setItems(null);
      return;
    }
    listSavedResearch(session.access_token)
      .then(setItems)
      .catch(() => setError(true));
  }, [session]);

  async function handleDelete(id: string) {
    if (!session) return;
    setItems((prev) => prev?.filter((x) => x.id !== id) ?? null);
    try {
      await deleteSavedResearch(session.access_token, id);
    } catch {
      // best effort: item already removed from view; a refresh will resync
    }
  }

  return (
    <div className="page">
      <div className="header">
        <div className="brand">
          <h1>{t.appName}</h1>
        </div>
        <div className="header-actions">
          <Link className="nav-link" href="/search">
            {t.navSearch}
          </Link>
          <Link className="nav-link" href="/action-plans">
            {t.navPlaybooks}
          </Link>
          <Link className="nav-link" href="/">
            {t.navChat}
          </Link>
          <AuthWidget lang={lang} />
          <button className="lang-toggle" onClick={() => setLang(lang === "en" ? "ne" : "en")}>
            {t.langToggle}
          </button>
        </div>
      </div>

      <div className="search-body">
        {!authLoading && !session && <div className="empty-state">{t.signInToSave}</div>}
        {session && items === null && !error && <div className="empty-state">…</div>}
        {error && <div className="empty-state">{t.error}</div>}
        {items && items.length === 0 && <div className="empty-state">{t.savedEmpty}</div>}
        {items && items.length > 0 && (
          <div className="results-list">
            {items.map((item) => (
              <div className="result-card saved-card" key={item.id}>
                <div className="result-title">{item.question}</div>
                <div className="result-snippet saved-answer">{item.answer.answer.slice(0, 400)}</div>
                <div className="saved-row">
                  <span className="saved-date">{new Date(item.created_at).toLocaleDateString()}</span>
                  <button className="save-button" onClick={() => handleDelete(item.id)}>
                    {t.deleteSaved}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
