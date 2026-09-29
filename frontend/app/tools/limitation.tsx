"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ErrorBox, errorText, Loading } from "@/components/ui";
import {
  Calendar,
  computeDeadline,
  DeadlineResult,
  entryHaystack,
  formatAd,
  formatBs,
  getLimitationCatalog,
  LimitationCatalog,
  LimitationCategory,
  LimitationEntry,
  lawHref,
  matchesQuery,
} from "@/lib/tools";
import { CalendarToggle, CalcError, Card, CitationLink, Citations, DateInput, Kv, Pill, SelectField, Submit, useCalc, useTools } from "./common";
import styles from "./tools.module.css";

/** Loads the limitation catalog once (the page and the section share it). */
export function useLimitationCatalog() {
  const [catalog, setCatalog] = useState<LimitationCatalog | null>(null);
  const [error, setError] = useState<unknown | null>(null);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let alive = true;
    setError(null);
    getLimitationCatalog()
      .then((c) => alive && setCatalog(c))
      .catch((e) => alive && setError(e));
    return () => {
      alive = false;
    };
  }, [attempt]);
  return { catalog, error, reload: () => setAttempt((n) => n + 1) };
}

/** Searchable text of every entry, for the filters and the page-wide search. */
export function buildHaystacks(catalog: LimitationCatalog): Map<string, string> {
  const map = new Map<string, string>();
  for (const cat of catalog.categories) for (const e of cat.entries) map.set(e.id, entryHaystack(e, cat.name));
  return map;
}

function periodClass(e: LimitationEntry): string {
  return e.period.kind === "fixed" ? styles.period : styles.periodNone;
}

// ---- the deadline calculator (used in a table row and in the quick card) -----------------------------

export function DeadlineCalculator({ entry, testId, defaultCalendar = "bs" }: { entry: LimitationEntry; testId: string; defaultCalendar?: Calendar }) {
  const { lang, t, s } = useTools();
  const [calendar, setCalendar] = useState<Calendar>(defaultCalendar);
  const [date, setDate] = useState("");
  const [longStop, setLongStop] = useState("");
  const [st, run] = useCalc<DeadlineResult>();
  const r = st.result;
  const stem = `dl-${entry.id}-${testId}`;

  if (!entry.computable) {
    return <div className={styles.note}>{s.tlNoCompute}</div>;
  }
  return (
    <div className={styles.calcBox}>
      <form
        className="form"
        onSubmit={(e) => {
          e.preventDefault();
          if (!date) return;
          run(() => computeDeadline({ claim_id: entry.id, trigger_date: date, calendar, long_stop_date: longStop || undefined }));
        }}
      >
        <CalendarToggle id={stem} value={calendar} onChange={(c) => { setCalendar(c); setDate(""); setLongStop(""); }} />
        <div className={styles.inlineFields}>
          <DateInput key={`s-${calendar}`} id={`${stem}-start`} label={s.tlStartDateBs} adLabel={t.calcTriggerDate} calendar={calendar} onChange={setDate} />
          {entry.long_stop && (
            <DateInput
              key={`l-${calendar}`}
              id={`${stem}-long`}
              label={`${s.tlLongStop}: ${entry.long_stop.start[lang]}`}
              calendar={calendar}
              onChange={setLongStop}
              optional
            />
          )}
        </div>
        {entry.start && <div className={styles.note}>{`${s.tlStartsFrom}: ${entry.start[lang]}`}</div>}
        {entry.start?.offset_days ? <div className={styles.note}>{s.tlOffsetNote(entry.start.offset_days)}</div> : null}
        {entry.long_stop && <div className={styles.note}>{s.tlLongStopHelp}</div>}
        <Submit busy={st.busy} disabled={!date} />
      </form>
      {st.error !== null && <CalcError error={st.error} />}
      {r && (
        <div className="result-box" role="status" data-testid={testId}>
          <Pill kind={r.is_time_barred ? "bad" : "ok"}>{r.is_time_barred ? t.calcTimeBarred : t.calcWithinTime}</Pill>
          <Kv
            rows={[
              [s.tlPeriodLabel, r.period.text[lang]],
              [s.tlDeadlineBs, formatBs(r.deadline_bs, lang)],
              [s.tlDeadlineAd, formatAd(r.deadline, lang)],
              [r.days_remaining < 0 ? s.tlDaysAgo : t.calcDaysLeft, String(Math.abs(r.days_remaining))],
              ...(r.long_stop ? ([[s.tlOuterLimit, formatBs(r.long_stop.deadline_bs, lang)]] as [string, string][]) : []),
            ]}
          />
          {r.needs_review && <div className={styles.warn}>{s.tlNeedsReview}</div>}
          <div className={styles.note}>{r.counting_note[lang]}</div>
          <Citations result={r} />
        </div>
      )}
    </div>
  );
}

// ---- the quick "pick a claim" card (keeps the original calculator's labels) ---------------------------------

function QuickCard({ catalog }: { catalog: LimitationCatalog }) {
  const { lang, t, s } = useTools();
  const groups = useMemo(
    () => catalog.categories.map((c) => ({ ...c, entries: c.entries.filter((e) => e.computable) })).filter((c) => c.entries.length > 0),
    [catalog],
  );
  // start on the most common claim (a contract / civil money claim), else the first one listed
  const flat = groups.flatMap((g) => g.entries);
  const first = (flat.find((e) => e.id === "contract_civil_claim") ?? flat[0])?.id ?? "";
  const [id, setId] = useState(first);
  const entry = flat.find((e) => e.id === (id || first)) ?? flat[0];
  return (
    <Card id="limitation" title={t.calcLimitation} desc={t.calcLimitationDesc}>
      <div className="form">
        <SelectField id="lim-type" label={t.calcClaimType} value={id || first} onChange={setId} help={s.tlQuickHelp}>
          {groups.map((g) => (
            <optgroup key={g.id} label={g.name[lang]}>
              {g.entries.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name[lang]} ({e.period.text[lang]})
                </option>
              ))}
            </optgroup>
          ))}
        </SelectField>
        {entry && <DeadlineCalculator key={entry.id} entry={entry} testId="limitation-result" defaultCalendar="ad" />}
      </div>
    </Card>
  );
}

// ---- the explorer table --------------------------------------------------------------------------------------------

function EntryRows({ entry, open, onToggle }: { entry: LimitationEntry; open: boolean; onToggle: () => void }) {
  const { lang, s } = useTools();
  const c = entry.citation;
  const lawName = lang === "ne" ? c.law_title_ne : (c.law_en ?? c.law_title_ne);
  const label = `${lawName} · ${lang === "ne" ? "दफा" : "s."} ${c.section}${c.clause ? ` ${c.clause}` : ""}`;
  return (
    <>
      <tr className={styles.entryRow} data-testid="limitation-row">
        <td data-label={s.tlColClaim}>
          <div className={styles.claimName}>
            {entry.name[lang]}
            {entry.needs_review && (
              <span className={styles.review} title={s.tlNeedsReview} aria-label={s.tlNeedsReview}>
                ⚠
              </span>
            )}
          </div>
          {entry.applies_to && <div className={styles.claimSub}>{entry.applies_to[lang]}</div>}
          {!entry.computable && entry.notes && <div className={styles.claimSub}>{entry.notes[lang]}</div>}
        </td>
        <td data-label={s.tlColPeriod}>
          <span className={periodClass(entry)}>{entry.period.text[lang]}</span>
          {entry.long_stop && (
            <div className={styles.claimSub}>
              + {s.tlOuterLimit}: {entry.long_stop.text[lang]}
            </div>
          )}
        </td>
        <td data-label={s.tlColStart}>
          {entry.start ? entry.start[lang] : "-"}
          {entry.start?.offset_days ? <div className={styles.claimSub}>{s.tlOffsetNote(entry.start.offset_days)}</div> : null}
        </td>
        <td data-label={s.tlColLaw}>
          {c.slug ? <Link href={lawHref({ slug: c.slug, section: c.section })}>{label}</Link> : label}
        </td>
        <td data-label={s.tlColAction}>
          {entry.computable ? (
            <button type="button" className="btn btn-small" aria-expanded={open} onClick={onToggle}>
              {open ? s.tlHide : s.tlCalcMyDeadline}
            </button>
          ) : (
            <span className="muted">-</span>
          )}
        </td>
      </tr>
      {open && (
        <tr className={styles.expand}>
          <td colSpan={5}>
            <DeadlineCalculator entry={entry} testId="limitation-row-result" />
            {entry.notes && entry.computable && <div className={styles.note} style={{ marginTop: 8 }}>{entry.notes[lang]}</div>}
            {entry.needs_review && <div className={styles.warn} style={{ marginTop: 8 }}>{s.tlNeedsReview}</div>}
          </td>
        </tr>
      )}
    </>
  );
}

function GeneralRules({ catalog }: { catalog: LimitationCatalog }) {
  const { lang, s } = useTools();
  return (
    <details className="card">
      <summary style={{ cursor: "pointer", fontWeight: 600 }}>{s.tlHowCounted}</summary>
      <ul className={styles.rules} style={{ marginTop: 10 }}>
        {catalog.general_rules.map((r) => (
          <li key={r.id}>
            {r.text[lang]}
            {r.citation && <CitationLink p={r.citation} />}
          </li>
        ))}
      </ul>
    </details>
  );
}

export function LimitationSection({
  catalog,
  error,
  reload,
  query,
  haystacks,
}: {
  catalog: LimitationCatalog | null;
  error: unknown | null;
  reload: () => void;
  query: string;
  haystacks: Map<string, string> | null;
}) {
  const { lang, t, s } = useTools();
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("");
  const [kind, setKind] = useState("");
  const [open, setOpen] = useState<string | null>(null);

  const filtered: LimitationCategory[] = useMemo(() => {
    if (!catalog || !haystacks) return [];
    return catalog.categories
      .filter((c) => !cat || c.id === cat)
      .map((c) => ({
        ...c,
        entries: c.entries.filter((e) => {
          if (kind && e.period.kind !== kind) return false;
          const hay = haystacks.get(e.id) ?? "";
          return (!q || matchesQuery(hay, q)) && (!query || matchesQuery(hay, query));
        }),
      }))
      .filter((c) => c.entries.length > 0);
  }, [catalog, haystacks, q, cat, kind, query]);

  if (error !== null && !catalog) {
    return <ErrorBox message={errorText(error, t)} onRetry={reload} />;
  }
  if (!catalog) return <Loading />;

  const shown = filtered.reduce((n, c) => n + c.entries.length, 0);
  return (
    <>
      <QuickCard catalog={catalog} />
      <section className={`card ${styles.wide}`} aria-labelledby="lim-explorer-h" data-testid="limitation-explorer">
        <h3 id="lim-explorer-h">{s.tlLimTitle}</h3>
        <p className="lede" style={{ marginBottom: 12 }}>
          {s.tlLimDesc}
        </p>
        <div className={styles.filters}>
          <div className="field">
            <label htmlFor="lim-q">{s.tlLimSearch}</label>
            <input
              id="lim-q"
              className="input"
              type="search"
              value={q}
              placeholder={s.tlSearchPlaceholder}
              onChange={(e) => setQ(e.target.value)}
              autoComplete="off"
            />
            <span className="help">{s.tlLimSearchHelp}</span>
          </div>
          <SelectField id="lim-cat" label={s.tlLimCategory} value={cat} onChange={setCat}>
            <option value="">{s.tlLimAllCats}</option>
            {catalog.categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name[lang]} ({c.entries.length})
              </option>
            ))}
          </SelectField>
          <SelectField id="lim-kind" label={s.tlLimKind} value={kind} onChange={setKind}>
            <option value="">{s.tlLimKindAll}</option>
            <option value="fixed">{s.tlLimKindFixed}</option>
            <option value="none">{s.tlLimKindNone}</option>
            <option value="special">{s.tlLimKindSpecial}</option>
          </SelectField>
        </div>
        <div className={styles.count} role="status" aria-live="polite" data-testid="limitation-count" style={{ marginTop: 10 }}>
          {s.tlLimShowing} {shown} {s.tlLimOf} {catalog.total} {s.tlLimEntries}
        </div>
        {shown === 0 && <p className="muted">{s.tlLimNone}</p>}
        {filtered.map((c) => (
          <div key={c.id}>
            <div className={styles.groupHead}>
              <span>{c.name[lang]}</span>
              <span className={styles.count}>{s.tlGroupCount(c.entries.length)}</span>
            </div>
            <div className={styles.tableWrap}>
              <table className={styles.lim}>
                <thead>
                  <tr>
                    <th scope="col">{s.tlColClaim}</th>
                    <th scope="col">{s.tlColPeriod}</th>
                    <th scope="col">{s.tlColStart}</th>
                    <th scope="col">{s.tlColLaw}</th>
                    <th scope="col">{s.tlColAction}</th>
                  </tr>
                </thead>
                <tbody>
                  {c.entries.map((e) => (
                    <EntryRows key={e.id} entry={e} open={open === e.id} onToggle={() => setOpen(open === e.id ? null : e.id)} />
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </section>
      <div className={styles.wide}>
        <GeneralRules catalog={catalog} />
      </div>
    </>
  );
}
