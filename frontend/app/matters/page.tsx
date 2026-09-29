"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ErrorBox, errorText, formatDate, Loading, RequireAuth } from "@/components/ui";
import { createMatter, listMatters, Matter } from "@/lib/api";
import { useLang } from "@/lib/LangContext";

export default function MattersPage() {
  const { t } = useLang();
  return (
    <div className="page">
      <div className="content">
        <h2>{t.mattersTitle}</h2>
        <p className="lede">{t.mattersIntro}</p>
        <RequireAuth>{(session) => <MatterList token={session.access_token} />}</RequireAuth>
      </div>
    </div>
  );
}

function MatterList({ token }: { token: string }) {
  const { lang, t } = useLang();
  const [items, setItems] = useState<Matter[] | null>(null);
  const [error, setError] = useState<{ e: unknown } | null>(null);
  const [name, setName] = useState("");
  const [facts, setFacts] = useState("");
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<{ e: unknown } | null>(null);

  const load = useCallback(() => {
    setError(null);
    listMatters(token)
      .then(setItems)
      .catch((e) => setError({ e }));
  }, [token]);
  useEffect(load, [load]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setCreating(true);
    setCreateError(null);
    try {
      const m = await createMatter(token, { client_name: name.trim(), facts: facts.trim() || null });
      setItems((prev) => [m, ...(prev ?? [])]);
      setName("");
      setFacts("");
    } catch (err) {
      setCreateError({ e: err });
    } finally {
      setCreating(false);
    }
  }

  return (
    <>
      <form className="card form" onSubmit={handleCreate}>
        <h3>{t.mattersNew}</h3>
        <div className="field">
          <label htmlFor="m-name">{t.mattersClientName}</label>
          <input id="m-name" className="input" value={name} maxLength={200} onChange={(e) => setName(e.target.value)} required />
        </div>
        <div className="field">
          <label htmlFor="m-facts">
            {t.mattersFacts} <span className="muted">({t.optional})</span>
          </label>
          <textarea id="m-facts" className="textarea" value={facts} onChange={(e) => setFacts(e.target.value)} />
        </div>
        {createError && <ErrorBox message={errorText(createError.e, t)} />}
        <div>
          <button className="btn btn-primary" type="submit" disabled={creating || !name.trim()}>
            {creating ? t.saving : t.mattersCreate}
          </button>
        </div>
      </form>

      {error && <ErrorBox message={errorText(error.e, t)} onRetry={load} />}
      {!error && items === null && <Loading />}
      {items && items.length === 0 && <div className="notice">{t.mattersEmpty}</div>}
      {items && items.length > 0 && (
        <ul className="list" data-testid="matter-list">
          {items.map((m) => (
            <li key={m.id}>
              <Link className="card card-link" href={`/matters/${m.id}`}>
                <div className="row row-between">
                  <div className="card-title">{m.client_name}</div>
                  <span className={`pill ${m.status === "closed" ? "" : "ok"}`}>
                    {m.status === "closed" ? t.mattersStatusClosed : t.mattersStatusOpen}
                  </span>
                </div>
                {m.facts && <div className="card-sub">{m.facts.length > 160 ? `${m.facts.slice(0, 160)}…` : m.facts}</div>}
                <div className="muted" style={{ marginTop: 6 }}>
                  {t.mattersUpdated} {formatDate(m.updated_at, lang)}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
