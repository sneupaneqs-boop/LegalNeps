"use client";

import Link from "next/link";
import { useState } from "react";
import { ErrorBox, errorText } from "@/components/ui";
import { ApiError, ResolvedProvision } from "@/lib/api";
import { toolsStrings, ToolsStrings } from "@/lib/i18n-tools";
import { useLang } from "@/lib/LangContext";
import { BS_MONTHS_EN, BS_MONTHS_NE, bsIso, Calendar, lawHref, provisionsOf } from "@/lib/tools";
import styles from "./tools.module.css";

/** Language, the shared strings and the tools-page strings in one hook. */
export function useTools() {
  const { lang, t } = useLang();
  return { lang, t, s: toolsStrings[lang] as ToolsStrings };
}

export type CalcState<R> = { busy: boolean; error: unknown | null; result: R | null };

// Shared plumbing for every calculator card: busy flag, error, result.
export function useCalc<R>(): [CalcState<R>, (run: () => Promise<R>) => Promise<void>] {
  const [state, setState] = useState<CalcState<R>>({ busy: false, error: null, result: null });
  async function run(fn: () => Promise<R>) {
    setState((s) => ({ ...s, busy: true, error: null }));
    try {
      const result = await fn();
      setState({ busy: false, error: null, result });
    } catch (e) {
      setState({ busy: false, error: e, result: null });
    }
  }
  return [state, run];
}

export function CalcError({ error }: { error: unknown }) {
  const { t } = useLang();
  // 400 = the server rejected the values (or the date is outside the calendar table); show its message
  const text =
    error instanceof ApiError && (error.status === 400 || error.status === 404 || error.status === 422) && error.detail
      ? `${t.calcInputError} (${error.detail})`
      : errorText(error, t);
  return <ErrorBox message={text} />;
}

export function parseNum(v: string): number | null {
  if (v.trim() === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

export function Card({ title, desc, id, children }: { title: string; desc?: string; id: string; children: React.ReactNode }) {
  return (
    <section className="card" aria-labelledby={`${id}-h`} data-testid={`calc-${id}`}>
      <h3 id={`${id}-h`}>{title}</h3>
      {desc && (
        <p className="lede" style={{ marginBottom: 12 }}>
          {desc}
        </p>
      )}
      {children}
    </section>
  );
}

export function NumField({
  id,
  label,
  value,
  onChange,
  step,
  help,
  min,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  step?: string;
  help?: string;
  min?: string;
}) {
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        className="input"
        type="number"
        inputMode="decimal"
        min={min ?? "0"}
        step={step ?? "any"}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      {help && <span className="help">{help}</span>}
    </div>
  );
}

export function SelectField({
  id,
  label,
  value,
  onChange,
  children,
  help,
  disabled,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  children: React.ReactNode;
  help?: string;
  disabled?: boolean;
}) {
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <select id={id} className="select" value={value} onChange={(e) => onChange(e.target.value)} disabled={disabled}>
        {children}
      </select>
      {help && <span className="help">{help}</span>}
    </div>
  );
}

export function CheckField({ id, label, checked, onChange }: { id: string; label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <label className={styles.checkRow} htmlFor={id}>
      <input id={id} type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <span>{label}</span>
    </label>
  );
}

export function Submit({ busy, disabled, label }: { busy: boolean; disabled: boolean; label?: string }) {
  const { t } = useLang();
  return (
    <div>
      <button className="btn btn-primary" type="submit" disabled={busy || disabled}>
        {busy ? t.calculating : (label ?? t.calculate)}
      </button>
    </div>
  );
}

export function Pill({ kind, children }: { kind: "ok" | "warn" | "bad"; children: React.ReactNode }) {
  return (
    <div className={`pill ${kind}`} style={{ alignSelf: "flex-start" }}>
      {children}
    </div>
  );
}

/** A cited provision that links to our own /law/<slug>/<section> page (section encoded), plus the official source. */
export function CitationLink({ p }: { p: ResolvedProvision }) {
  const { lang, t } = useLang();
  const note = p.note?.[lang] || p.note?.en || p.note?.ne;
  return (
    <div className={`provision ${styles.cite}`}>
      <Link href={lawHref(p)}>{p.citation}</Link>
      {p.url && (
        <>
          {" · "}
          <a href={p.url} target="_blank" rel="noopener noreferrer">
            {t.officialSourceLink}
          </a>
        </>
      )}
      {note && <div>{note}</div>}
    </div>
  );
}

/** Every provision cited anywhere in a tool result. */
export function Citations({ result }: { result: unknown }) {
  const { s } = useTools();
  const items = provisionsOf(result);
  if (items.length === 0) return null;
  return (
    <div className={styles.citations} data-testid="citations">
      <div className="muted">{s.tlSource}</div>
      {items.map((p) => (
        <CitationLink key={`${p.slug}|${p.section ?? ""}`} p={p} />
      ))}
    </div>
  );
}

export function CalendarToggle({ value, onChange, id }: { value: Calendar; onChange: (c: Calendar) => void; id: string }) {
  const { s } = useTools();
  return (
    <div role="group" aria-label={s.tlCalendar} className={styles.inlineToggle} data-testid={`${id}-calendar`}>
      {(["bs", "ad"] as const).map((c) => (
        <button key={c} type="button" className={`btn btn-small${value === c ? " btn-primary" : ""}`} aria-pressed={value === c} onClick={() => onChange(c)}>
          {c === "bs" ? s.tlBs : s.tlAd}
        </button>
      ))}
    </div>
  );
}

/**
 * A date input in AD (native date picker) or BS (year / month / day). The parent
 * gets "YYYY-MM-DD" (in the chosen calendar) or "" while incomplete. Re-mount it
 * (key={calendar}) when the calendar changes.
 */
export function DateInput({
  id,
  label,
  calendar,
  onChange,
  adLabel,
  optional,
}: {
  id: string;
  label: string;
  calendar: Calendar;
  onChange: (iso: string) => void;
  adLabel?: string;
  optional?: boolean;
}) {
  const { lang, s } = useTools();
  const [y, setY] = useState("");
  const [m, setM] = useState("");
  const [d, setD] = useState("");
  const names = lang === "ne" ? BS_MONTHS_NE : BS_MONTHS_EN;
  const opt = optional ? ` (${s.tlOptional})` : "";
  if (calendar === "ad") {
    return (
      <div className="field">
        <label htmlFor={id}>{(adLabel ?? label) + opt}</label>
        <input id={id} className="input" type="date" onChange={(e) => onChange(e.target.value)} />
      </div>
    );
  }
  const update = (ny: string, nm: string, nd: string) => onChange(bsIso(ny, nm, nd));
  return (
    <fieldset style={{ border: "none", padding: 0, margin: 0, minWidth: 0 }} data-testid={`${id}-bs`}>
      <legend className="label" style={{ fontSize: 13, fontWeight: 600, padding: 0, marginBottom: 5 }}>
        {label + opt}
      </legend>
      <div className={styles.bsDate}>
        <input
          id={`${id}-y`}
          className="input"
          type="number"
          inputMode="numeric"
          min="1975"
          max="2100"
          step="1"
          placeholder={s.tlYearBs}
          aria-label={`${label}: ${s.tlYearBs}`}
          value={y}
          onChange={(e) => {
            setY(e.target.value);
            update(e.target.value, m, d);
          }}
        />
        <select
          id={`${id}-m`}
          className="select"
          aria-label={`${label}: ${s.tlMonthBs}`}
          value={m}
          onChange={(e) => {
            setM(e.target.value);
            update(y, e.target.value, d);
          }}
        >
          <option value="">{s.tlMonthBs}</option>
          {names.map((n, i) => (
            <option key={n} value={String(i + 1)}>
              {i + 1} · {n}
            </option>
          ))}
        </select>
        <input
          id={`${id}-d`}
          className="input"
          type="number"
          inputMode="numeric"
          min="1"
          max="32"
          step="1"
          placeholder={s.tlDayBs}
          aria-label={`${label}: ${s.tlDayBs}`}
          value={d}
          onChange={(e) => {
            setD(e.target.value);
            update(y, m, e.target.value);
          }}
        />
      </div>
    </fieldset>
  );
}

export function Kv({ rows }: { rows: [string, React.ReactNode][] }) {
  return (
    <dl className="kv">
      {rows.map(([k, v]) => (
        <span key={k} style={{ display: "contents" }}>
          <dt>{k}</dt>
          <dd>{v}</dd>
        </span>
      ))}
    </dl>
  );
}
