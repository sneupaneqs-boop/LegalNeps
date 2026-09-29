"use client";

import { useEffect, useState } from "react";
import { formatNpr } from "@/components/ui";
import {
  adToBs,
  Bilingual,
  bsToAd,
  calcGratuity,
  calcNotice,
  calcSeverance,
  DateConversion,
  estimateAppealFee,
  estimateCourtFee,
} from "@/lib/api";
import { preetiToUnicode } from "@/lib/preeti";
import { Calendar, formatAd, toolGet } from "@/lib/tools";
import {
  CalcError,
  CalendarToggle,
  Card,
  CheckField,
  Citations,
  DateInput,
  Kv,
  NumField,
  parseNum,
  Pill,
  SelectField,
  Submit,
  useCalc,
  useTools,
} from "./common";
import styles from "./tools.module.css";

// ============================================================================================
// A small config-driven form card: fields -> API call -> rendered result + citations
// ============================================================================================

type Vals = Record<string, string | boolean>;
type Show = (v: Vals) => boolean;
type Field =
  | { t: "num"; k: string; label: string; step?: string; opt?: boolean; def?: string; help?: string; show?: Show; min?: string }
  | { t: "sel"; k: string; label: string; opts: [string, string][]; def: string; help?: string; show?: Show }
  | { t: "chk"; k: string; label: string; def: boolean; show?: Show }
  | { t: "date"; k: string; label: string; opt?: boolean; show?: Show };

function initial(fields: Field[]): Vals {
  const v: Vals = {};
  for (const f of fields) v[f.k] = f.t === "chk" ? f.def : f.t === "num" || f.t === "sel" ? (f.def ?? "") : "";
  return v;
}

function FormTool<R>({
  id,
  title,
  desc,
  fields,
  calendar,
  submit,
  render,
  above,
  testId,
}: {
  id: string;
  title: string;
  desc: string;
  fields: Field[];
  calendar?: boolean;
  submit: (v: Vals, cal: Calendar) => Promise<R>;
  render: (r: R) => React.ReactNode;
  above?: React.ReactNode;
  testId?: string;
}) {
  const { s } = useTools();
  const [vals, setVals] = useState<Vals>(() => initial(fields));
  const [cal, setCal] = useState<Calendar>("bs");
  const [st, run] = useCalc<R>();
  const set = (k: string, v: string | boolean) => setVals((o) => ({ ...o, [k]: v }));
  const visible = (f: Field) => !f.show || f.show(vals);
  const missing = fields.some((f) => {
    if (!visible(f) || f.t === "chk" || f.t === "sel") return false;
    const optional = f.opt === true;
    const value = String(vals[f.k] ?? "");
    if (f.t === "num") return !optional && parseNum(value) === null;
    return !optional && value === "";
  });
  const hasDates = fields.some((f) => f.t === "date");

  return (
    <Card id={id} title={title} desc={desc}>
      {above}
      <form
        className="form"
        onSubmit={(e) => {
          e.preventDefault();
          if (!missing) run(() => submit(vals, cal));
        }}
      >
        {calendar && hasDates && (
          <CalendarToggle
            id={id}
            value={cal}
            onChange={(c) => {
              setCal(c);
              setVals((o) => {
                const n = { ...o };
                for (const f of fields) if (f.t === "date") n[f.k] = "";
                return n;
              });
            }}
          />
        )}
        {fields.map((f) => {
          if (!visible(f)) return null;
          const key = `${id}-${f.k}`;
          if (f.t === "num") {
            return (
              <NumField
                key={key}
                id={key}
                label={f.opt ? `${f.label} (${s.tlOptional})` : f.label}
                value={String(vals[f.k] ?? "")}
                onChange={(v) => set(f.k, v)}
                step={f.step}
                help={f.help}
                min={f.min}
              />
            );
          }
          if (f.t === "sel") {
            return (
              <SelectField key={key} id={key} label={f.label} value={String(vals[f.k])} onChange={(v) => set(f.k, v)} help={f.help}>
                {f.opts.map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </SelectField>
            );
          }
          if (f.t === "chk") {
            return <CheckField key={key} id={key} label={f.label} checked={vals[f.k] === true} onChange={(v) => set(f.k, v)} />;
          }
          return <DateInput key={`${key}-${cal}`} id={key} label={f.label} calendar={cal} onChange={(v) => set(f.k, v)} optional={f.opt} />;
        })}
        <Submit busy={st.busy} disabled={missing} />
      </form>
      {st.error !== null && <CalcError error={st.error} />}
      {st.result !== null && (
        <div className="result-box" role="status" data-testid={testId ?? `${id}-result`}>
          {render(st.result)}
          <Citations result={st.result} />
        </div>
      )}
    </Card>
  );
}

const num = (v: string | boolean | undefined): number | undefined => (typeof v === "string" && v.trim() !== "" && Number.isFinite(Number(v)) ? Number(v) : undefined);
const dateOrUndef = (v: string | boolean | undefined): string | undefined => (typeof v === "string" && v ? v : undefined);
const pct = (n: number) => `${n.toLocaleString("en-IN", { maximumFractionDigits: 4 })}%`;
const days = (n: number) => n.toLocaleString("en-IN", { maximumFractionDigits: 2 });

/** ISO AD date plus the BS date the API also returns, when it does. */
function DatePair({ ad, bs, lang }: { ad: string; bs?: string | null; lang: "en" | "ne" }) {
  return (
    <span>
      {formatAd(ad, lang)} {bs ? <span className="muted">({bs} BS)</span> : null}
    </span>
  );
}

// ============================================================================================
// Labour & employment
// ============================================================================================

type OvertimeResult = {
  hourly_basic_pay: number;
  overtime_rate_per_hour: number;
  overtime_pay_npr: number;
  hours: number;
  period: "day" | "week";
  legal_limit_hours: number;
  within_legal_limit: boolean;
  hourly_basis: Bilingual;
};

export function OvertimeCard() {
  const { lang, s } = useTools();
  return (
    <FormTool<OvertimeResult>
      id="overtime"
      title={s.tlOvertimeTitle}
      desc={s.tlOvertimeDesc}
      fields={[
        { t: "num", k: "hours", label: s.tlOvertimeHours },
        { t: "sel", k: "period", label: s.tlOvertimePeriod, def: "day", opts: [["day", s.tlPerDay], ["week", s.tlPerWeek]] },
        { t: "sel", k: "basis", label: s.tlPayBasis, def: "monthly", opts: [["monthly", s.tlMonthly], ["hourly", s.tlHourly]] },
        { t: "num", k: "hourly", label: s.tlHourlyPay, show: (v) => v.basis === "hourly" },
        { t: "num", k: "monthly", label: s.tlMonthly + " (NPR)", show: (v) => v.basis === "monthly" },
        { t: "num", k: "paid_days", label: s.tlPaidDays, help: s.tlPaidDaysHelp, show: (v) => v.basis === "monthly", step: "any" },
      ]}
      submit={(v) =>
        toolGet<OvertimeResult>("/labour/overtime", {
          overtime_hours: num(v.hours),
          period: String(v.period),
          basic_hourly_pay: v.basis === "hourly" ? num(v.hourly) : undefined,
          basic_monthly_pay: v.basis === "monthly" ? num(v.monthly) : undefined,
          paid_days_per_month: v.basis === "monthly" ? num(v.paid_days) : undefined,
        })
      }
      render={(r) => (
        <>
          <div className="big-number">{formatNpr(r.overtime_pay_npr)}</div>
          <Pill kind={r.within_legal_limit ? "ok" : "bad"}>{r.within_legal_limit ? s.tlWithinLimit : s.tlOverLimit}</Pill>
          <Kv
            rows={[
              [s.tlHourlyRate, formatNpr(r.hourly_basic_pay)],
              [s.tlOvertimeRate, formatNpr(r.overtime_rate_per_hour)],
              [s.tlLegalLimit, `${r.legal_limit_hours} / ${r.period === "day" ? s.tlPerDay : s.tlPerWeek}`],
            ]}
          />
          <div className={styles.note}>{r.hourly_basis[lang]}</div>
        </>
      )}
    />
  );
}

type HoursResult = { within_limits: boolean; issues: { code: string }[]; break_needed: boolean };

export function HoursCard() {
  const { s } = useTools();
  const issueText: Record<string, string> = {
    day_over_8: s.tlIssueDay,
    week_over_48: s.tlIssueWeek,
    overtime_day_over_4: s.tlIssueOtDay,
    overtime_week_over_24: s.tlIssueOtWeek,
  };
  return (
    <FormTool<HoursResult>
      id="hours"
      title={s.tlHoursTitle}
      desc={s.tlHoursDesc}
      fields={[
        { t: "num", k: "day", label: s.tlHoursDay },
        { t: "num", k: "week", label: s.tlHoursWeek, opt: true },
        { t: "num", k: "otday", label: s.tlOtDay, opt: true },
        { t: "num", k: "otweek", label: s.tlOtWeek, opt: true },
      ]}
      submit={(v) =>
        toolGet<HoursResult>("/labour/hours/check", {
          hours_per_day: num(v.day),
          hours_per_week: num(v.week),
          overtime_per_day: num(v.otday),
          overtime_per_week: num(v.otweek),
        })
      }
      render={(r) => (
        <>
          <Pill kind={r.within_limits ? "ok" : "bad"}>{r.within_limits ? s.tlAllWithin : s.tlOverLimit}</Pill>
          {r.issues.map((i) => (
            <div key={i.code}>{issueText[i.code] ?? i.code}</div>
          ))}
          {r.break_needed && <div className={styles.note}>{s.tlBreakDue}</div>}
        </>
      )}
    />
  );
}

type LeaveTable = {
  entitlements: { id: string; days: number; unit: string; paid: boolean | string; name: Bilingual; note?: Bilingual }[];
  accumulation: { home_leave_cap_days: number; sick_leave_cap_days: number };
};

export function LeaveTableCard() {
  const { lang, s } = useTools();
  const [st, run] = useCalc<LeaveTable>();
  const r = st.result;
  return (
    <Card id="leave" title={s.tlLeaveTitle} desc={s.tlLeaveDesc}>
      {!r && (
        <button type="button" className="btn btn-primary" disabled={st.busy} onClick={() => run(() => toolGet<LeaveTable>("/labour/leave"))}>
          {s.tlShowTable}
        </button>
      )}
      {st.error !== null && <CalcError error={st.error} />}
      {r && (
        <div className="result-box" data-testid="leave-result">
          <table className={styles.smallTable}>
            <thead>
              <tr>
                <th>{s.tlLeaveName}</th>
                <th className={styles.num}>{s.tlLeaveDays}</th>
              </tr>
            </thead>
            <tbody>
              {r.entitlements.map((e) => (
                <tr key={e.id}>
                  <td>
                    {e.name[lang]}
                    {e.note && <div className="muted">{e.note[lang]}</div>}
                  </td>
                  <td className={styles.num}>
                    {e.days}
                    <div className="muted">{e.unit}</div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className={styles.note}>{s.tlLeaveCaps(r.accumulation.home_leave_cap_days, r.accumulation.sick_leave_cap_days)}</div>
          <Citations result={r} />
        </div>
      )}
    </Card>
  );
}

type AccrualResult = {
  home_leave_days: number;
  home_leave_whole_days: number;
  home_leave_over_cap_days: number;
  sick_leave_days?: number;
};

export function AccrualCard() {
  const { s } = useTools();
  return (
    <FormTool<AccrualResult>
      id="accrual"
      title={s.tlAccrualTitle}
      desc={s.tlAccrualDesc}
      fields={[
        { t: "num", k: "days", label: s.tlDaysWorked },
        { t: "num", k: "months", label: s.tlMonthsInYear, opt: true },
      ]}
      submit={(v) => toolGet<AccrualResult>("/labour/leave/accrual", { days_worked: num(v.days), months_worked_in_year: num(v.months) })}
      render={(r) => (
        <Kv
          rows={[
            [s.tlHomeLeaveEarned, days(r.home_leave_days)],
            [s.tlHomeLeaveWhole, String(r.home_leave_whole_days)],
            ...(r.home_leave_over_cap_days > 0 ? ([[s.tlOverCap, days(r.home_leave_over_cap_days)]] as [string, string][]) : []),
            ...(r.sick_leave_days !== undefined ? ([[s.tlSickLeaveYear, days(r.sick_leave_days)]] as [string, string][]) : []),
          ]}
        />
      )}
    />
  );
}

type EncashResult = { home_leave_days_counted: number; sick_leave_days_counted: number; amount_npr: number };

export function EncashCard() {
  const { s } = useTools();
  return (
    <FormTool<EncashResult>
      id="encash"
      title={s.tlEncashTitle}
      desc={s.tlEncashDesc}
      fields={[
        { t: "num", k: "home", label: s.tlHomeDays },
        { t: "num", k: "sick", label: s.tlSickDays },
        { t: "num", k: "daily", label: s.tlDailyBasic },
      ]}
      submit={(v) => toolGet<EncashResult>("/labour/leave/encashment", { home_leave_days: num(v.home), sick_leave_days: num(v.sick), daily_basic_pay: num(v.daily) })}
      render={(r) => (
        <>
          <div className="big-number">{formatNpr(r.amount_npr)}</div>
          <Kv rows={[[s.tlCountedHome, days(r.home_leave_days_counted)], [s.tlCountedSick, days(r.sick_leave_days_counted)]]} />
        </>
      )}
    />
  );
}

type MaternityResult = {
  latest_start: string;
  minimum_leave_until: string;
  leave_start: string;
  leave_end: string;
  leave_start_bs: string;
  leave_end_bs: string;
  full_pay_days: number;
  full_pay_until: string;
  paternity_days: number;
  warnings: string[];
  extra_unpaid_month: { from: string; to: string } | null;
};

export function MaternityCard() {
  const { lang, s } = useTools();
  return (
    <FormTool<MaternityResult>
      id="maternity"
      title={s.tlMaternityTitle}
      desc={s.tlMaternityDesc}
      calendar
      fields={[
        { t: "date", k: "edd", label: s.tlEdd },
        { t: "date", k: "start", label: s.tlLeaveStart, opt: true },
        { t: "chk", k: "extra", label: s.tlExtraMonth, def: false },
      ]}
      submit={(v, cal) =>
        toolGet<MaternityResult>("/labour/maternity", {
          expected_delivery: dateOrUndef(v.edd),
          calendar: cal,
          leave_start: dateOrUndef(v.start),
          extra_month_recommended: v.extra === true ? "true" : undefined,
        })
      }
      render={(r) => (
        <>
          <Kv
            rows={[
              [s.tlLatestStart, <DatePair key="a" ad={r.latest_start} lang={lang} />],
              [s.tlLeaveRange, (
                <span key="b">
                  <DatePair ad={r.leave_start} bs={r.leave_start_bs} lang={lang} /> → <DatePair ad={r.leave_end} bs={r.leave_end_bs} lang={lang} />
                </span>
              )],
              [s.tlMinUntil, <DatePair key="c" ad={r.minimum_leave_until} lang={lang} />],
              [s.tlFullPayDays, `${r.full_pay_days}`],
              [s.tlFullPayUntil, <DatePair key="d" ad={r.full_pay_until} lang={lang} />],
              [s.tlPaternityDays, `${r.paternity_days}`],
              ...(r.extra_unpaid_month
                ? ([[s.tlExtraLeave, <span key="e">{formatAd(r.extra_unpaid_month.from, lang)} → {formatAd(r.extra_unpaid_month.to, lang)}</span>]] as [string, React.ReactNode][])
                : []),
            ]}
          />
          {r.warnings.includes("start_after_latest_start") && <div className={styles.warn}>{s.tlWarnStartLate}</div>}
          {r.warnings.includes("ends_before_six_weeks_after_expected_delivery") && <div className={styles.warn}>{s.tlWarnEndsEarly}</div>}
        </>
      )}
    />
  );
}

type FestivalResult = { amount_npr: number };

export function FestivalCard() {
  const { s, t } = useTools();
  return (
    <FormTool<FestivalResult>
      id="festival"
      title={s.tlFestivalTitle}
      desc={s.tlFestivalDesc}
      fields={[
        { t: "num", k: "pay", label: t.calcBasicPay },
        { t: "num", k: "months", label: s.tlMonthsServed, def: "12" },
      ]}
      submit={(v) => toolGet<FestivalResult>("/labour/festival-allowance", { basic_monthly_pay: num(v.pay), months_of_service: num(v.months) })}
      render={(r) => (
        <>
          <div className="big-number">{formatNpr(r.amount_npr)}</div>
          <div className="muted">{s.tlAllowance}</div>
        </>
      )}
    />
  );
}

type FundResult = {
  monthly: { employee_pf_npr: number; employer_pf_npr: number; employer_gratuity_npr: number; total_deposit_npr: number; employer_cost_npr: number };
  period_total: { employee_pf_npr: number; employer_pf_npr: number; employer_gratuity_npr: number; total_deposit_npr: number; employer_cost_npr: number };
  note: Bilingual;
};

export function FundCard() {
  const { lang, s, t } = useTools();
  return (
    <FormTool<FundResult>
      id="fund"
      title={s.tlFundTitle}
      desc={s.tlFundDesc}
      fields={[
        { t: "num", k: "pay", label: t.calcBasicPay },
        { t: "num", k: "months", label: s.tlMonthsCount, def: "1" },
      ]}
      submit={(v) => toolGet<FundResult>("/labour/fund-contributions", { basic_monthly_pay: num(v.pay), months: num(v.months) })}
      render={(r) => {
        const rows: [string, keyof FundResult["monthly"]][] = [
          [s.tlEmployeePf, "employee_pf_npr"],
          [s.tlEmployerPf, "employer_pf_npr"],
          [s.tlEmployerGratuity, "employer_gratuity_npr"],
          [s.tlTotalDeposit, "total_deposit_npr"],
          [s.tlEmployerCost, "employer_cost_npr"],
        ];
        return (
          <>
            <table className={styles.smallTable}>
              <thead>
                <tr>
                  <th />
                  <th className={styles.num}>{s.tlPerMonth}</th>
                  <th className={styles.num}>{s.tlForPeriod}</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(([label, key]) => (
                  <tr key={key}>
                    <td>{label}</td>
                    <td className={styles.num}>{formatNpr(r.monthly[key])}</td>
                    <td className={styles.num}>{formatNpr(r.period_total[key])}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className={styles.note}>{r.note[lang]}</div>
          </>
        );
      }}
    />
  );
}

type TiersResult = { tiers: { service: Bilingual; notice_days: number }[]; note: Bilingual };

export function TiersCard() {
  const { lang, s } = useTools();
  const [st, run] = useCalc<TiersResult>();
  const r = st.result;
  return (
    <Card id="notice-tiers" title={s.tlTiersTitle} desc={s.tlTiersDesc}>
      {!r && (
        <button type="button" className="btn btn-primary" disabled={st.busy} onClick={() => run(() => toolGet<TiersResult>("/labour/notice-tiers"))}>
          {s.tlShowTable}
        </button>
      )}
      {st.error !== null && <CalcError error={st.error} />}
      {r && (
        <div className="result-box" data-testid="notice-tiers-result">
          <table className={styles.smallTable}>
            <thead>
              <tr>
                <th>{s.tlTiersService}</th>
                <th className={styles.num}>{s.tlTiersNotice}</th>
              </tr>
            </thead>
            <tbody>
              {r.tiers.map((x) => (
                <tr key={x.notice_days}>
                  <td>{x.service[lang]}</td>
                  <td className={styles.num}>{x.notice_days}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className={styles.note}>{r.note[lang]}</div>
          <Citations result={r} />
        </div>
      )}
    </Card>
  );
}

// ---- the original labour cards (unchanged behaviour) -------------------------------------------------------------

export function GratuityCard() {
  const { t } = useTools();
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
          <Citations result={r} />
        </div>
      )}
    </Card>
  );
}

export function NoticeCard() {
  const { t } = useTools();
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
          <Kv rows={[[t.calcNoticeDays, String(r.notice_period_days)], [t.calcPayInLieu, formatNpr(r.pay_in_lieu_npr)]]} />
          <Citations result={r} />
        </div>
      )}
    </Card>
  );
}

export function SeveranceCard() {
  const { t } = useTools();
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
          <Citations result={r} />
        </div>
      )}
    </Card>
  );
}

// ============================================================================================
// Money & interest
// ============================================================================================

type InterestRules = { rules: Bilingual[] };
type InterestResult = {
  days: number;
  rate_applied_pct: number;
  interest_npr: number;
  total_due_npr: number;
  capped_by_principal: boolean;
  interest_at_agreed_rate_npr: number | null;
  excess_over_legal_max_npr: number | null;
  rate_basis: Bilingual;
  day_count: Bilingual;
  start_date_bs: string;
  end_date_bs: string;
};

function InterestRulesList() {
  const { lang, s } = useTools();
  const [rules, setRules] = useState<InterestRules | null>(null);
  useEffect(() => {
    let alive = true;
    toolGet<InterestRules>("/interest/rules")
      .then((r) => alive && setRules(r))
      .catch(() => {});
    return () => {
      alive = false;
    };
  }, []);
  if (!rules) return null;
  return (
    <details style={{ marginBottom: 12 }}>
      <summary style={{ cursor: "pointer", fontSize: 13.5 }}>{s.tlInterestRules}</summary>
      <ul className={styles.rules} style={{ marginTop: 8 }}>
        {rules.rules.map((r) => (
          <li key={r.en}>{r[lang]}</li>
        ))}
      </ul>
      <Citations result={rules} />
    </details>
  );
}

export function InterestCard() {
  const { lang, s } = useTools();
  return (
    <FormTool<InterestResult>
      id="interest"
      title={s.tlInterestTitle}
      desc={s.tlInterestDesc}
      calendar
      above={<InterestRulesList />}
      fields={[
        { t: "num", k: "principal", label: s.tlPrincipal },
        { t: "date", k: "start", label: s.tlFromDate },
        { t: "date", k: "end", label: s.tlToDate },
        { t: "num", k: "rate", label: s.tlAgreedRate, opt: true, help: s.tlAgreedRateHelp },
        { t: "chk", k: "stated", label: s.tlInterestStated, def: true },
      ]}
      submit={(v, cal) =>
        toolGet<InterestResult>("/interest/simple", {
          principal: num(v.principal),
          start_date: dateOrUndef(v.start),
          end_date: dateOrUndef(v.end),
          calendar: cal,
          rate: num(v.rate),
          interest_stated: v.stated === true ? "true" : "false",
        })
      }
      render={(r) => (
        <>
          <div className="big-number">{formatNpr(r.interest_npr)}</div>
          <Kv
            rows={[
              [s.tlDaysCount, String(r.days)],
              [s.tlRateApplied, pct(r.rate_applied_pct)],
              [s.tlTotalDue, formatNpr(r.total_due_npr)],
              ...(r.interest_at_agreed_rate_npr !== null ? ([[s.tlAtAgreed, formatNpr(r.interest_at_agreed_rate_npr)]] as [string, string][]) : []),
              ...(r.excess_over_legal_max_npr !== null ? ([[s.tlExcess, formatNpr(r.excess_over_legal_max_npr)]] as [string, string][]) : []),
            ]}
          />
          {r.capped_by_principal && <div className={styles.warn}>{s.tlCapped}</div>}
          <div className={styles.note}>{r.rate_basis[lang]}</div>
          <div className={styles.note}>{r.day_count[lang]}</div>
        </>
      )}
    />
  );
}

// ============================================================================================
// Tax
// ============================================================================================

type TaxResult = {
  resident: boolean;
  tax_npr: number;
  effective_rate_pct: number;
  slabs: { from: number; to: number | null; rate_pct: number; income_in_slab: number; tax: number }[];
  deductions: { id: string; amount: number }[];
  rebate_npr?: number;
  note?: Bilingual;
};

export function IncomeTaxCard() {
  const { lang, s } = useTools();
  return (
    <FormTool<TaxResult>
      id="income-tax"
      title={s.tlIncomeTaxTitle}
      desc={s.tlIncomeTaxDesc}
      fields={[
        { t: "num", k: "income", label: s.tlTaxableIncome },
        { t: "chk", k: "resident", label: s.tlResident, def: true },
        { t: "chk", k: "exempt", label: s.tlFirstSlabExempt, def: false, show: (v) => v.resident === true },
        { t: "num", k: "insurance", label: s.tlInsurance, opt: true, show: (v) => v.resident === true },
        { t: "num", k: "remote", label: s.tlRemote, opt: true, show: (v) => v.resident === true },
        { t: "chk", k: "disabled", label: s.tlDisabled, def: false, show: (v) => v.resident === true },
        { t: "chk", k: "woman", label: s.tlWomanSalary, def: false, show: (v) => v.resident === true },
      ]}
      submit={(v) =>
        toolGet<TaxResult>("/tax/income", {
          taxable_income: num(v.income),
          resident: v.resident === true,
          first_slab_exempt: v.exempt === true,
          insurance_premium: num(v.insurance),
          remote_allowance: num(v.remote),
          disabled: v.disabled === true,
          woman_salary_only: v.woman === true,
        })
      }
      render={(r) => (
        <>
          <div className="big-number">{formatNpr(r.tax_npr)}</div>
          <Kv rows={[[s.tlEffective, pct(r.effective_rate_pct)], ...(r.rebate_npr ? ([[s.tlRebate, formatNpr(r.rebate_npr)]] as [string, string][]) : [])]} />
          {r.slabs.length > 0 && (
            <table className={styles.smallTable}>
              <thead>
                <tr>
                  <th>{s.tlSlab}</th>
                  <th className={styles.num}>{s.tlIncomeInSlab}</th>
                  <th className={styles.num}>{s.tlRateCol}</th>
                  <th className={styles.num}>{s.tlTaxCol}</th>
                </tr>
              </thead>
              <tbody>
                {r.slabs.map((x) => (
                  <tr key={x.from}>
                    <td>{`${x.from.toLocaleString("en-IN")} – ${x.to === null ? "∞" : x.to.toLocaleString("en-IN")}`}</td>
                    <td className={styles.num}>{formatNpr(x.income_in_slab)}</td>
                    <td className={styles.num}>{pct(x.rate_pct)}</td>
                    <td className={styles.num}>{formatNpr(x.tax)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {r.deductions.length > 0 && (
            <div className={styles.note}>
              {s.tlDeductions}: {r.deductions.map((d) => `${d.id} ${formatNpr(d.amount)}`).join(", ")}
            </div>
          )}
          {r.note && <div className={styles.note}>{r.note[lang]}</div>}
        </>
      )}
    />
  );
}

type TdsType = { id: string; rate_pct: number; name: Bilingual };
type TdsResult = { rate_pct: number; tds_npr: number; net_payable_npr: number; applies: boolean; reason: Bilingual | null };

export function TdsCard() {
  const { lang, s } = useTools();
  const [types, setTypes] = useState<TdsType[] | null>(null);
  const [err, setErr] = useState<unknown | null>(null);
  useEffect(() => {
    let alive = true;
    toolGet<TdsType[]>("/tax/tds-types")
      .then((x) => alive && setTypes(x))
      .catch((e) => alive && setErr(e));
    return () => {
      alive = false;
    };
  }, []);
  if (err !== null) return <Card id="tds" title={s.tlTdsTitle} desc={s.tlTdsDesc}><CalcError error={err} /></Card>;
  if (!types) return <Card id="tds" title={s.tlTdsTitle} desc={s.tlTdsDesc}><div className="muted">…</div></Card>;
  return (
    <FormTool<TdsResult>
      id="tds"
      title={s.tlTdsTitle}
      desc={s.tlTdsDesc}
      fields={[
        { t: "sel", k: "type", label: s.tlPaymentType, def: types[0]?.id ?? "default", opts: types.map((x) => [x.id, `${x.name[lang]} (${x.rate_pct}%)`] as [string, string]) },
        { t: "num", k: "amount", label: s.tlPaymentAmount },
        { t: "num", k: "agg", label: s.tlAggregated, opt: true, show: (v) => v.type === "contract" },
      ]}
      submit={(v) => toolGet<TdsResult>("/tax/tds", { payment_type: String(v.type), amount: num(v.amount), aggregated_amount: v.type === "contract" ? num(v.agg) : undefined })}
      render={(r) => (
        <>
          <div className="big-number">{formatNpr(r.tds_npr)}</div>
          <Kv rows={[[s.tlTdsRate, pct(r.rate_pct)], [s.tlNetPayable, formatNpr(r.net_payable_npr)]]} />
          {!r.applies && <div className={styles.note}>{r.reason ? r.reason[lang] : s.tlNoTds}</div>}
        </>
      )}
    />
  );
}

// ============================================================================================
// Court fees
// ============================================================================================

export function CourtFeeCard() {
  const { t } = useTools();
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
          <Kv rows={[[t.calcFilingFee, formatNpr(r.filing_fee_npr)], [t.calcCourtFeeAmount, formatNpr(r.court_fee_npr)]]} />
          <Citations result={r} />
        </div>
      )}
    </Card>
  );
}

export function AppealFeeCard() {
  const { t } = useTools();
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
          <Citations result={r} />
        </div>
      )}
    </Card>
  );
}

type FlatType = { id: string; fee_npr: number; name: Bilingual };
type FlatResult = { court_fee_npr: number; filing_fee_npr: number; total_npr: number };

export function FlatFeeCard() {
  const { lang, s } = useTools();
  const [types, setTypes] = useState<FlatType[] | null>(null);
  const [err, setErr] = useState<unknown | null>(null);
  useEffect(() => {
    let alive = true;
    toolGet<FlatType[]>("/court-fee/flat-types")
      .then((x) => alive && setTypes(x))
      .catch((e) => alive && setErr(e));
    return () => {
      alive = false;
    };
  }, []);
  if (err !== null) return <Card id="flat-fee" title={s.tlFlatTitle} desc={s.tlFlatDesc}><CalcError error={err} /></Card>;
  if (!types) return <Card id="flat-fee" title={s.tlFlatTitle} desc={s.tlFlatDesc}><div className="muted">…</div></Card>;
  return (
    <FormTool<FlatResult>
      id="flat-fee"
      title={s.tlFlatTitle}
      desc={s.tlFlatDesc}
      fields={[{ t: "sel", k: "type", label: s.tlCaseType, def: types[0]?.id ?? "", opts: types.map((x) => [x.id, `${x.name[lang]} (${formatNpr(x.fee_npr)})`] as [string, string]) }]}
      submit={(v) => toolGet<FlatResult>("/court-fee/flat", { case_type: String(v.type) })}
      render={(r) => (
        <>
          <div className="big-number">{formatNpr(r.total_npr)}</div>
          <Kv rows={[[s.tlFeeCourt, formatNpr(r.court_fee_npr)], [s.tlFeeFiling, formatNpr(r.filing_fee_npr)]]} />
        </>
      )}
    />
  );
}

export function ReviewFeeCard() {
  const { s } = useTools();
  return (
    <FormTool<{ review_fee_npr: number }>
      id="review-fee"
      title={s.tlReviewTitle}
      desc={s.tlReviewDesc}
      fields={[{ t: "num", k: "value", label: s.tlContested }]}
      submit={(v) => toolGet<{ review_fee_npr: number }>("/court-fee/review", { contested_value: num(v.value) })}
      render={(r) => <div className="big-number">{formatNpr(r.review_fee_npr)}</div>}
    />
  );
}

export function SettlementFeeCard() {
  const { s } = useTools();
  return (
    <FormTool<{ retained_npr: number; refunded_npr: number }>
      id="settlement-fee"
      title={s.tlSettlementTitle}
      desc={s.tlSettlementDesc}
      fields={[
        { t: "num", k: "paid", label: s.tlFeePaid },
        { t: "sel", k: "stage", label: s.tlStage, def: "before", opts: [["before", s.tlStageBefore], ["after", s.tlStageAfter]] },
      ]}
      submit={(v) => toolGet<{ retained_npr: number; refunded_npr: number }>("/court-fee/settlement", { fee_paid: num(v.paid), before_evidence: v.stage === "before" })}
      render={(r) => (
        <>
          <div className="big-number">{formatNpr(r.refunded_npr)}</div>
          <Kv rows={[[s.tlRefunded, formatNpr(r.refunded_npr)], [s.tlRetained, formatNpr(r.retained_npr)]]} />
        </>
      )}
    />
  );
}

// ============================================================================================
// Dates
// ============================================================================================

export function DateCard() {
  const { t } = useTools();
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

type AddResult = { result: string; result_bs: string; start_bs: string; counting_note: Bilingual };

export function DateAddCard() {
  const { lang, s } = useTools();
  return (
    <FormTool<AddResult>
      id="date-add"
      title={s.tlAddTitle}
      desc={s.tlAddDesc}
      calendar
      fields={[
        { t: "date", k: "date", label: s.tlDateLabel },
        { t: "num", k: "years", label: s.tlAddYears, def: "0", step: "1", min: "-300", help: s.tlAddHelp },
        { t: "num", k: "months", label: s.tlAddMonths, def: "0", step: "1", min: "-3600" },
        { t: "num", k: "days", label: s.tlAddDays, def: "0", step: "1", min: "-110000" },
      ]}
      submit={(v, cal) =>
        toolGet<AddResult>("/date/add", { date: dateOrUndef(v.date), calendar: cal, years: num(v.years) ?? 0, months: num(v.months) ?? 0, days: num(v.days) ?? 0 })
      }
      render={(r) => (
        <>
          <Kv rows={[[s.tlResultDate + " (BS)", r.result_bs], [s.tlResultDate + " (AD)", formatAd(r.result, lang)]]} />
          <div className={styles.note}>{r.counting_note[lang]}</div>
        </>
      )}
    />
  );
}

type DiffResult = { years: number; months: number; days: number; total_days: number; end_is_before_start: boolean };

export function DateDiffCard() {
  const { s } = useTools();
  return (
    <FormTool<DiffResult>
      id="date-diff"
      title={s.tlDiffTitle}
      desc={s.tlDiffDesc}
      calendar
      fields={[
        { t: "date", k: "start", label: s.tlFromDate },
        { t: "date", k: "end", label: s.tlToDate },
      ]}
      submit={(v, cal) => toolGet<DiffResult>("/date/difference", { start: dateOrUndef(v.start), end: dateOrUndef(v.end), calendar: cal })}
      render={(r) => (
        <>
          <Kv
            rows={[
              [s.tlYmd, `${r.years} ${s.tlYearsUnit}, ${r.months} ${s.tlMonthsUnit}, ${r.days} ${s.tlDaysUnit}`],
              [s.tlTotalDays, String(r.total_days)],
            ]}
          />
          {r.end_is_before_start && <div className={styles.warn}>{s.tlEndBefore}</div>}
        </>
      )}
    />
  );
}

type AgeResult = {
  years: number;
  months: number;
  days: number;
  total_days: number;
  thresholds: { years: number; reached: boolean; reached_on: string | null; reached_on_bs: string | null; label: Bilingual }[];
};

export function AgeCard() {
  const { lang, s } = useTools();
  return (
    <FormTool<AgeResult>
      id="age"
      title={s.tlAgeTitle}
      desc={s.tlAgeDesc}
      calendar
      fields={[
        { t: "date", k: "birth", label: s.tlBirthDate },
        { t: "date", k: "asof", label: s.tlAsOf, opt: true },
      ]}
      submit={(v, cal) => toolGet<AgeResult>("/date/age", { birth_date: dateOrUndef(v.birth), calendar: cal, as_of: dateOrUndef(v.asof) })}
      render={(r) => (
        <>
          <div className="big-number">{`${r.years} ${s.tlYearsUnit}, ${r.months} ${s.tlMonthsUnit}, ${r.days} ${s.tlDaysUnit}`}</div>
          <table className={styles.smallTable}>
            <tbody>
              {r.thresholds.map((x) => (
                <tr key={x.years}>
                  <td>
                    <strong>{x.years}</strong> · {x.label[lang]}
                  </td>
                  <td>
                    {x.reached ? s.tlReached : s.tlNotYet}
                    {x.reached_on && <div className="muted">{`${s.tlOn} ${x.reached_on_bs ?? ""} BS · ${formatAd(x.reached_on, lang)}`}</div>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    />
  );
}

// ============================================================================================
// Converters
// ============================================================================================

export function PreetiCard() {
  const { t } = useTools();
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
