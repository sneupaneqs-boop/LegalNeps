"use client";

import { useEffect, useState } from "react";
import { deleteSavedResearch, listSavedResearch, SavedResearch } from "@/lib/api";
import { strings } from "@/lib/i18n";
import { useLang } from "@/lib/LangContext";
import { useAuth } from "@/lib/useAuth";

export default function SavedPage() {
  const { lang } = useLang();
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
      <div className="search-body">
        <h2 className="law-title">{t.navSaved}</h2>
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
