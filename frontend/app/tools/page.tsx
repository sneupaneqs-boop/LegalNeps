"use client";

import { useEffect, useState } from "react";
import { ErrorBox, errorText, formatNpr, Provision } from "@/components/ui";
import {
  adToBs,
  ApiError,
  bsToAd,
  calcGratuity,
  calcNotice,
  calcSeverance,
  checkLimitation,
  DateConversion,
  estimateAppealFee,
  estimateCourtFee,
  listClaimTypes,
} from "@/lib/api";
import { useLang } from "@/lib/LangContext";
import { preetiToUnicode } from "@/lib/preeti";

type CalcState<R> = { busy: boolean; error: unknown | null; result: R | null };

// Shared plumbing for every calculator card: busy flag, error, result.
function useCalc<R>(): [CalcState<R>, (run: () => Promise<R>) => Promise<void>] {
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

function CalcError({ error }: { error: unknown }) {
  const { t } = useLang();
  // 400 = the server rejected the numbers; show its message
  const text =
    error instanceof ApiError && error.status === 400 && error.detail
      ? `${t.calcInputError} (${error.detail})`
      : errorText(error, t);
  return <ErrorBox message={text} />;
}

function parseNum(v: string): number | null {
  if (v.trim() === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function Card({ title, desc, id, children }: { title: string; desc: string; id: string; children: React.ReactNode }) {
  return (
    <section className="card" aria-labelledby={`${id}-h`} data-testid={`calc-${id}`}>
      <h3 id={`${id}-h`}>{title}</h3>
      <p className="lede" style={{ marginBottom: 12 }}>
        {desc}
      </p>
      {children}
    </section>
  );
}

function NumField({ id, label, value, onChange, step }: { id: string; label: string; value: string; onChange: (v: string) => void; step?: string }) {
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <input id={id} className="input" type="number" inputMode="decimal" min="0" step={step ?? "any"} value={value} onChange={(e) => onChange(e.target.value)} />
    </div>
  );
}

function Submit({ busy, disabled }: { busy: boolean; disabled: boolean }) {
  const { t } = useLang();
  return (
    <div>
      <button className="btn btn-primary" type="submit" disabled={busy || disabled}>
        {busy ? t.calculating : t.calculate}
      </button>
    </div>
  );
}

export default function ToolsPage() {
  const { t } = useLang();
  return (
    <div className="page">
      <div className="content">
        <h2>{t.toolsTitle}</h2>
        <p className="lede">{t.toolsIntro}</p>
        <div className="card-grid" style={{ alignItems: "start" }}>
          <LimitationCard />
          <CourtFeeCard />
          <AppealFeeCard />
          <GratuityCard />
          <NoticeCard />
          <SeveranceCard />
          <DateCard />
          <PreetiCard />
        </div>
      </div>
    </div>
  );
}

function LimitationCard() {
  const { lang, t } = useLang();
  const [types, setTypes] = useState<string[] | null>(null);
  const [typesError, setTypesError] = useState<unknown | null>(null);
  const [claim, setClaim] = useState("");
  const [date, setDate] = useState("");
  const [st, run] = useCalc<Awaited<ReturnType<typeof checkLimitation>>>();

  useEffect(() => {
    listClaimTypes()
      .then((ts) => {
        setTypes(ts);
        setClaim((c) => c || ts[0] || "");
      })
      .catch(setTypesError);
  }, []);

  const label = (id: string) => t.claimTypes[id] ?? id.replace(/_/g, " ");
  const r = st.result;

  return (
    <Card id="limitation" title={t.calcLimitation} desc={t.calcLimitationDesc}>
      {typesError !== null && <CalcError error={typesError} />}
      <form
        className="form"
        onSubmit={(e) => {
          e.preventDefault();
          run(() => checkLimitation(claim, date));
        }}
      >
        <div className="field">
          <label htmlFor="lim-type">{t.calcClaimType}</label>
          <select id="lim-type" className="select" value={claim} onChange={(e) => setClaim(e.target.value)} disabled={!types}>
            {(types ?? []).map((id) => (
              <option key={id} value={id}>
                {label(id)}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="lim-date">{t.calcTriggerDate}</label>
          <input id="lim-date" className="input" type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </div>
        <Submit busy={st.busy} disabled={!claim || !date} />
      </form>
      {st.error !== null && <CalcError error={st.error} />}
      {r && (
        <div className="result-box" role="status" data-testid="limitation-result">
          <div className={`pill ${r.is_time_barred ? "bad" : "ok"}`} style={{ alignSelf: "flex-start" }}>
            {r.is_time_barred ? t.calcTimeBarred : t.calcWithinTime}
          </div>
          <dl className="kv">
            <dt>{t.calcDeadline}</dt>
            <dd>{r.deadline}</dd>
            <dt>{t.calcDaysLeft}</dt>
            <dd>{r.days_remaining}</dd>
          </dl>
          <div>{r.note[lang]}</div>
          <Provision p={r.provision} lang={lang} />
        </div>
      )}
    </Card>
  );
}

function CourtFeeCard() {
  const { lang, t } = useLang();
  const [value, setValue] = useState("");
  const [st, run] = useCalc<Awaited<ReturnType<typeof estimateCourtFee>>>();
  const n = parseNum(value);
  const r = st.result;
  return (
    <Card id="court-fee" title={t.calcCourtFee} desc={t.calcCourtFeeDesc}>
      <form
        className="form"
        onSubmit={(e) => {
          e.preventDefault();
          if (n !== null) run(() => estimateCourtFee(n));
        }}
      >
        <NumField id="cf-value" label={t.calcClaimValue} value={value} onChange={setValue} />
        <Submit busy={st.busy} disabled={n === null} />
      </form>
      {st.error !== null && <CalcError error={st.error} />}
      {r && (
        <div className="result-box" role="status" data-testid="court-fee-result">
          <div className="big-number">{formatNpr(r.total_npr)}</div>
          <dl className="kv">
            <dt>{t.calcFilingFee}</dt>
            <dd>{formatNpr(r.filing_fee_npr)}</dd>
          </dl>
          <Provision p={r.filing_fee_provision} lang={lang} />
          <dl className="kv">
            <dt>{t.calcCourtFeeAmount}</dt>
            <dd>{formatNpr(r.court_fee_npr)}</dd>
          </dl>
          <Provision p={r.court_fee_provision} lang={lang} />
        </div>
      )}
    </Card>
  );
}

function AppealFeeCard() {
  const { lang, t } = useLang();
  const [value, setValue] = useState("");
  const [st, run] = useCalc<Awaited<ReturnType<typeof estimateAppealFee>>>();
  const n = parseNum(value);
  const r = st.result;
  return (
    <Card id="appeal-fee" title={t.calcAppealFee} desc={t.calcAppealFeeDesc}>
      <form
        className="form"
        onSubmit={(e) => {
          e.preventDefault();
          if (n !== null) run(() => estimateAppealFee(n));
        }}
      >
        <NumField id="af-value" label={t.calcDisputedValue} value={value} onChange={setValue} />
        <Submit busy={st.busy} disabled={n === null} />
      </form>
      {st.error !== null && <CalcError error={st.error} />}
      {r && (
        <div className="result-box" role="status" data-testid="appeal-fee-result">
          <div className="big-number">{formatNpr(r.appeal_fee_npr)}</div>
          <Provision p={r.provision} lang={lang} />
        </div>
      )}
    </Card>
  );
}

function GratuityCard() {
  const { lang, t } = useLang();
  const [pay, setPay] = useState("");
  const [months, setMonths] = useState("");
  const [st, run] = useCalc<Awaited<ReturnType<typeof calcGratuity>>>();
  const p = parseNum(pay);
  const m = parseNum(months);
  const r = st.result;
  return (
    <Card id="gratuity" title={t.calcGratuity} desc={t.calcGratuityDesc}>
      <form
        className="form"
        onSubmit={(e) => {
          e.preventDefault();
          if (p !== null && m !== null) run(() => calcGratuity(p, m));
        }}
      >
        <NumField id="gr-pay" label={t.calcBasicPay} value={pay} onChange={setPay} />
        <NumField id="gr-months" label={t.calcMonths} value={months} onChange={setMonths} />
        <Submit busy={st.busy} disabled={p === null || m === null} />
      </form>
      {st.error !== null && <CalcError error={st.error} />}
      {r && (
        <div className="result-box" role="status" data-testid="gratuity-result">
          <div className="big-number">{formatNpr(r.amount_npr)}</div>
          <Provision p={r.provision} lang={lang} />
        </div>
      )}
    </Card>
  );
}

function NoticeCard() {
  const { lang, t } = useLang();
  const [days, setDays] = useState("");
  const [wage, setWage] = useState("");
  const [st, run] = useCalc<Awaited<ReturnType<typeof calcNotice>>>();
  const d = parseNum(days);
  const w = parseNum(wage);
  const r = st.result;
  return (
    <Card id="notice" title={t.calcNotice} desc={t.calcNoticeDesc}>
      <form
        className="form"
        onSubmit={(e) => {
          e.preventDefault();
          // the API takes whole days of service
          if (d !== null && w !== null) run(() => calcNotice(Math.floor(d), w));
        }}
      >
        <NumField id="no-days" label={t.calcServiceDays} value={days} onChange={setDays} step="1" />
        <NumField id="no-wage" label={t.calcDailyWage} value={wage} onChange={setWage} />
        <Submit busy={st.busy} disabled={d === null || w === null} />
      </form>
      {st.error !== null && <CalcError error={st.error} />}
      {r && (
        <div className="result-box" role="status" data-testid="notice-result">
          <dl className="kv">
            <dt>{t.calcNoticeDays}</dt>
            <dd>{r.notice_period_days}</dd>
            <dt>{t.calcPayInLieu}</dt>
            <dd>{formatNpr(r.pay_in_lieu_npr)}</dd>
          </dl>
          <Provision p={r.provision} lang={lang} />
        </div>
      )}
    </Card>
  );
}

function SeveranceCard() {
  const { lang, t } = useLang();
  const [pay, setPay] = useState("");
  const [years, setYears] = useState("");
  const [st, run] = useCalc<Awaited<ReturnType<typeof calcSeverance>>>();
  const p = parseNum(pay);
  const y = parseNum(years);
  const r = st.result;
  return (
    <Card id="severance" title={t.calcSeverance} desc={t.calcSeveranceDesc}>
      <form
        className="form"
        onSubmit={(e) => {
          e.preventDefault();
          if (p !== null && y !== null) run(() => calcSeverance(p, y));
        }}
      >
        <NumField id="sv-pay" label={t.calcBasicPay} value={pay} onChange={setPay} />
        <NumField id="sv-years" label={t.calcYears} value={years} onChange={setYears} />
        <Submit busy={st.busy} disabled={p === null || y === null} />
      </form>
      {st.error !== null && <CalcError error={st.error} />}
      {r && (
        <div className="result-box" role="status" data-testid="severance-result">
          <div className="big-number">{formatNpr(r.amount_npr)}</div>
          <Provision p={r.provision} lang={lang} />
        </div>
      )}
    </Card>
  );
}

function DateCard() {
  const { t } = useLang();
  const [mode, setMode] = useState<"bs" | "ad">("bs");
  const [y, setY] = useState("");
  const [m, setM] = useState("");
  const [d, setD] = useState("");
  const [ad, setAd] = useState("");
  const [st, run] = useCalc<DateConversion>();

  const yn = parseNum(y);
  const mn = parseNum(m);
  const dn = parseNum(d);
  const ready = mode === "bs" ? yn !== null && mn !== null && dn !== null : ad !== "";
  const r = st.result;

  return (
    <Card id="date" title={t.calcDate} desc={t.calcDateDesc}>
      <div className="row" role="group" aria-label={t.calcDate} style={{ marginBottom: 12 }}>
        <button type="button" className={`btn btn-small${mode === "bs" ? " btn-primary" : ""}`} aria-pressed={mode === "bs"} onClick={() => setMode("bs")}>
          {t.calcBsToAd}
        </button>
        <button type="button" className={`btn btn-small${mode === "ad" ? " btn-primary" : ""}`} aria-pressed={mode === "ad"} onClick={() => setMode("ad")}>
          {t.calcAdToBs}
        </button>
      </div>
      <form
        className="form"
        onSubmit={(e) => {
          e.preventDefault();
          if (mode === "bs" && yn !== null && mn !== null && dn !== null) run(() => bsToAd(yn, mn, dn));
          if (mode === "ad" && ad) run(() => adToBs(ad));
        }}
      >
        {mode === "bs" ? (
          <div className="row" style={{ alignItems: "flex-start", flexWrap: "nowrap" }}>
            <NumField id="dt-y" label={t.calcYear} value={y} onChange={setY} step="1" />
            <NumField id="dt-m" label={t.calcMonth} value={m} onChange={setM} step="1" />
            <NumField id="dt-d" label={t.calcDay} value={d} onChange={setD} step="1" />
          </div>
        ) : (
          <div className="field">
            <label htmlFor="dt-ad">{t.calcAdDate}</label>
            <input id="dt-ad" className="input" type="date" value={ad} onChange={(e) => setAd(e.target.value)} />
          </div>
        )}
        <Submit busy={st.busy} disabled={!ready} />
      </form>
      {st.error !== null && <CalcError error={st.error} />}
      {r && (
        <div className="result-box" role="status" data-testid="date-result">
          <dl className="kv">
            <dt>{t.calcBsResult}</dt>
            <dd data-testid="date-bs">
              {r.bs.year}-{String(r.bs.month).padStart(2, "0")}-{String(r.bs.day).padStart(2, "0")}
            </dd>
            <dt>{t.calcAdResult}</dt>
            <dd data-testid="date-ad">{r.ad}</dd>
          </dl>
        </div>
      )}
    </Card>
  );
}

function PreetiCard() {
  const { t } = useLang();
  const [text, setText] = useState("");
  const [copied, setCopied] = useState(false);
  const out = preetiToUnicode(text);

  async function copy() {
    try {
      await navigator.clipboard.writeText(out);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // clipboard blocked: the output box is selectable, so the user can copy by hand
    }
  }

  return (
    <Card id="preeti" title={t.preetiTitle} desc={t.preetiDesc}>
      <div className="form">
        <div className="field">
          <label htmlFor="pr-in">{t.preetiInput}</label>
          <textarea
            id="pr-in"
            className="textarea"
            value={text}
            placeholder={t.preetiPlaceholder}
            spellCheck={false}
            autoCapitalize="off"
            autoCorrect="off"
            onChange={(e) => setText(e.target.value)}
          />
        </div>
        <div className="field">
          <label htmlFor="pr-out">{t.preetiOutput}</label>
          <textarea id="pr-out" className="textarea" lang="ne" readOnly value={out} data-testid="preeti-output" />
        </div>
        <div className="row">
          <button type="button" className="btn btn-primary" disabled={!out} onClick={copy}>
            {copied ? t.preetiCopied : t.preetiCopy}
          </button>
          <button type="button" className="btn" disabled={!text} onClick={() => setText("")}>
            {t.preetiClear}
          </button>
        </div>
        <div className="muted">{t.preetiNote}</div>
      </div>
    </Card>
  );
}
