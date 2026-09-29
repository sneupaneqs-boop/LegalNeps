"use client";

import { useState } from "react";
import { search, Source } from "@/lib/api";
import { strings } from "@/lib/i18n";
import { useLang } from "@/lib/LangContext";

const DOC_TYPES = ["act", "rule", "constitution", "order", "directive", "treaty", "other"] as const;

function docTypeLabel(t: Strings, key: string): string {
  const map: Record<string, string> = {
    act: t.docTypeAct, rule: t.docTypeRule, constitution: t.docTypeConstitution,
    order: t.docTypeOrder, directive: t.docTypeDirective, treaty: t.docTypeTreaty, other: t.docTypeOther,
  };
  return map[key] || key;
}

type Strings = (typeof strings)["en"];

function resultHref(s: Source): string {
  if (s.category === "law" && s.slug) {
    return s.section ? `/law/${s.slug}/${encodeURIComponent(s.section)}` : `/law/${s.slug}`;
  }
  return s.url || "#";
}

function ResultCard({ s, t }: { s: Source; t: Strings }) {
  const href = resultHref(s);
  const external = !(s.category === "law" && s.slug);
  return (
    <a
      className="result-card"
      href={href}
      target={external ? "_blank" : undefined}
      rel={external ? "noopener noreferrer" : undefined}
    >
      <div className="result-top">
        <span className={`badge ${s.category}`}>{s.category === "law" ? t.badgeLaw : t.badgePrecedent}</span>
        {s.doc_type && <span className="result-doctype">{docTypeLabel(t, s.doc_type)}</span>}
        {s.status === "bill" && <span className="badge bill">{t.statusBill}</span>}
      </div>
      <div className="result-title">{s.title || s.citation}</div>
      <div className="result-citation">{s.citation}</div>
      <div className="result-snippet">{s.snippet}</div>
    </a>
  );
}

export default function SearchPage() {
  const { lang } = useLang();
  const [q, setQ] = useState("");
  const [category, setCategory] = useState<"" | "law" | "precedent">("");
  const [docType, setDocType] = useState("");
  const [inForceOnly, setInForceOnly] = useState(true);
  const [results, setResults] = useState<Source[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const t = strings[lang];

  async function runSearch(query: string) {
    if (!query.trim()) return;
    setLoading(true);
    setError(false);
    try {
      const res = await search(query, {
        category: category || undefined,
        docType: docType || undefined,
        status: inForceOnly ? "in_force" : undefined,
        lang,
      });
      setResults(res.results);
    } catch {
      setError(true);
      setResults(null);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    runSearch(q);
  }

  return (
    <div className="page">
      <div className="search-body">
        <form className="search-form" onSubmit={handleSubmit}>
          <input
            className="search-input"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder={t.searchPlaceholder}
          />
          <button type="submit" disabled={loading || !q.trim()}>
            {t.searchButton}
          </button>
        </form>

        <div className="search-filters">
          <label className="filter">
            <span>{t.filterCategory}</span>
            <select value={category} onChange={(e) => setCategory(e.target.value as typeof category)}>
              <option value="">{t.filterAllCategories}</option>
              <option value="law">{t.badgeLaw}</option>
              <option value="precedent">{t.badgePrecedent}</option>
            </select>
          </label>
          <label className="filter">
            <span>{t.filterDocType}</span>
            <select value={docType} onChange={(e) => setDocType(e.target.value)}>
              <option value="">{t.filterAllDocTypes}</option>
              {DOC_TYPES.map((dt) => (
                <option key={dt} value={dt}>
                  {docTypeLabel(t, dt)}
                </option>
              ))}
            </select>
          </label>
          <label className="filter filter-checkbox">
            <input
              type="checkbox"
              checked={inForceOnly}
              onChange={(e) => setInForceOnly(e.target.checked)}
            />
            <span>{t.filterInForceOnly}</span>
          </label>
        </div>

        {results === null && !loading && !error && <div className="empty-state">{t.searchEmpty}</div>}
        {error && <div className="empty-state">{t.error}</div>}
        {results !== null && results.length === 0 && <div className="empty-state">{t.searchNoResults}</div>}
        {results && results.length > 0 && (
          <div className="results-list">
            {results.map((s) => (
              <ResultCard key={s.id} s={s} t={t} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
