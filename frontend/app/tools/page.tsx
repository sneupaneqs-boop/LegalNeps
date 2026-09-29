"use client";

import { useMemo, useState } from "react";
import { matchesQuery, searchForm } from "@/lib/tools";
import {
  AccrualCard,
  AgeCard,
  AppealFeeCard,
  CourtFeeCard,
  DateAddCard,
  DateCard,
  DateDiffCard,
  EncashCard,
  FestivalCard,
  FlatFeeCard,
  FundCard,
  GratuityCard,
  HoursCard,
  IncomeTaxCard,
  InterestCard,
  LeaveTableCard,
  MaternityCard,
  NoticeCard,
  OvertimeCard,
  PreetiCard,
  ReviewFeeCard,
  SettlementFeeCard,
  SeveranceCard,
  TdsCard,
  TiersCard,
} from "./calculators";
import { useTools } from "./common";
import { buildHaystacks, LimitationSection, useLimitationCatalog } from "./limitation";
import styles from "./tools.module.css";

type SectionId = "deadlines" | "labour" | "money" | "tax" | "court" | "dates" | "converters";

type Tool = { id: string; section: SectionId; meta: string; node: React.ReactNode };

export default function ToolsPage() {
  const { t, s } = useTools();
  const [query, setQuery] = useState("");
  const { catalog, error, reload } = useLimitationCatalog();
  const haystacks = useMemo(() => (catalog ? buildHaystacks(catalog) : null), [catalog]);

  const sections: { id: SectionId; title: string }[] = [
    { id: "deadlines", title: s.tlSecDeadlines },
    { id: "labour", title: s.tlSecLabour },
    { id: "money", title: s.tlSecMoney },
    { id: "tax", title: s.tlSecTax },
    { id: "court", title: s.tlSecCourt },
    { id: "dates", title: s.tlSecDates },
    { id: "converters", title: s.tlSecConverters },
  ];

  // What each calculator card is about, in English and Nepali, for the page-wide search.
  const tools: Tool[] = [
    { id: "overtime", section: "labour", meta: `${s.tlOvertimeTitle} ${s.tlOvertimeDesc} overtime extra hours 1.5 ओभरटाइम बढी समय`, node: <OvertimeCard key="overtime" /> },
    { id: "hours", section: "labour", meta: `${s.tlHoursTitle} ${s.tlHoursDesc} working hours 8 48 rest break काम गर्ने समय`, node: <HoursCard key="hours" /> },
    { id: "leave", section: "labour", meta: `${s.tlLeaveTitle} ${s.tlLeaveDesc} leave holiday sick home maternity paternity mourning बिदा`, node: <LeaveTableCard key="leave" /> },
    { id: "accrual", section: "labour", meta: `${s.tlAccrualTitle} ${s.tlAccrualDesc} leave accrual home leave sick leave बिदा`, node: <AccrualCard key="accrual" /> },
    { id: "encash", section: "labour", meta: `${s.tlEncashTitle} ${s.tlEncashDesc} leave encashment accumulated leave pay-out`, node: <EncashCard key="encash" /> },
    { id: "maternity", section: "labour", meta: `${s.tlMaternityTitle} ${s.tlMaternityDesc} maternity paternity pregnancy delivery प्रसूति`, node: <MaternityCard key="maternity" /> },
    { id: "festival", section: "labour", meta: `${s.tlFestivalTitle} ${s.tlFestivalDesc} dashain bonus festival allowance दशैं चाडपर्व`, node: <FestivalCard key="festival" /> },
    { id: "fund", section: "labour", meta: `${s.tlFundTitle} ${s.tlFundDesc} provident fund pf gratuity ssf social security सञ्चय कोष उपदान`, node: <FundCard key="fund" /> },
    { id: "notice", section: "labour", meta: `${t.calcNotice} ${t.calcNoticeDesc} notice termination resignation pay in lieu सूचना`, node: <NoticeCard key="notice" /> },
    { id: "tiers", section: "labour", meta: `${s.tlTiersTitle} ${s.tlTiersDesc} notice period service`, node: <TiersCard key="tiers" /> },
    { id: "gratuity", section: "labour", meta: `${t.calcGratuity} ${t.calcGratuityDesc} gratuity upadan उपदान`, node: <GratuityCard key="gratuity" /> },
    { id: "severance", section: "labour", meta: `${t.calcSeverance} ${t.calcSeveranceDesc} severance retrenchment layoff कटौती`, node: <SeveranceCard key="severance" /> },
    { id: "interest", section: "money", meta: `${s.tlInterestTitle} ${s.tlInterestDesc} interest loan lender borrower usury ब्याज ऋण साहू साँवा`, node: <InterestCard key="interest" /> },
    { id: "income-tax", section: "tax", meta: `${s.tlIncomeTaxTitle} ${s.tlIncomeTaxDesc} income tax slab salary आयकर कर`, node: <IncomeTaxCard key="income-tax" /> },
    { id: "tds", section: "tax", meta: `${s.tlTdsTitle} ${s.tlTdsDesc} tds withholding tax at source rent dividend contract`, node: <TdsCard key="tds" /> },
    { id: "court-fee", section: "court", meta: `${t.calcCourtFee} ${t.calcCourtFeeDesc} court fee filing fee plaint फिराद`, node: <CourtFeeCard key="court-fee" /> },
    { id: "appeal-fee", section: "court", meta: `${t.calcAppealFee} ${t.calcAppealFeeDesc} appeal fee punarabedan`, node: <AppealFeeCard key="appeal-fee" /> },
    { id: "flat-fee", section: "court", meta: `${s.tlFlatTitle} ${s.tlFlatDesc} flat fee divorce partition land registration injunction`, node: <FlatFeeCard key="flat-fee" /> },
    { id: "review-fee", section: "court", meta: `${s.tlReviewTitle} ${s.tlReviewDesc} review retrial`, node: <ReviewFeeCard key="review-fee" /> },
    { id: "settlement-fee", section: "court", meta: `${s.tlSettlementTitle} ${s.tlSettlementDesc} settlement milapatra refund`, node: <SettlementFeeCard key="settlement-fee" /> },
    { id: "date", section: "dates", meta: `${t.calcDate} ${t.calcDateDesc} bs ad convert bikram sambat gregorian मिति`, node: <DateCard key="date" /> },
    { id: "date-add", section: "dates", meta: `${s.tlAddTitle} ${s.tlAddDesc} add days months years bs date`, node: <DateAddCard key="date-add" /> },
    { id: "date-diff", section: "dates", meta: `${s.tlDiffTitle} ${s.tlDiffDesc} difference between dates duration`, node: <DateDiffCard key="date-diff" /> },
    { id: "age", section: "dates", meta: `${s.tlAgeTitle} ${s.tlAgeDesc} age majority adult minor consent marriage उमेर बालिग`, node: <AgeCard key="age" /> },
    { id: "preeti", section: "converters", meta: `${t.preetiTitle} ${t.preetiDesc} preeti unicode font converter प्रीति युनिकोड`, node: <PreetiCard key="preeti" /> },
  ];

  const q = searchForm(query);
  const limMeta = `${t.calcLimitation} ${t.calcLimitationDesc} ${s.tlLimTitle} ${s.tlLimDesc} limitation period deadline time limit statute of limitations हदम्याद म्याद`;
  const limToolMatch = !q || matchesQuery(searchForm(limMeta), q);
  // entries that match the query themselves (e.g. "cheque" finds the cheque-dishonour period)
  const limEntryMatches = useMemo(() => {
    if (!q || !catalog || !haystacks) return 0;
    let n = 0;
    for (const cat of catalog.categories) for (const e of cat.entries) if (matchesQuery(haystacks.get(e.id) ?? "", q)) n += 1;
    return n;
  }, [q, catalog, haystacks]);

  const visibleTools = tools.filter((tool) => !q || matchesQuery(searchForm(tool.meta), q));
  // the limitation section shows when its own metadata matches, or some entry matches (then only those entries)
  const showLimitation = limToolMatch || limEntryMatches > 0;
  const nothing = q !== "" && visibleTools.length === 0 && !showLimitation && !(catalog === null && error === null);

  const visibleSections = sections.filter((sec) => (sec.id === "deadlines" ? showLimitation : visibleTools.some((tool) => tool.section === sec.id)));

  return (
    <div className="page">
      <div className="content">
        <h2>{t.toolsTitle}</h2>
        <p className="lede">{t.toolsIntro}</p>
        <p className="lede">{s.tlEstimate}</p>

        <div className={styles.searchBar}>
          <div className={styles.searchRow}>
            <input
              className="input"
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={s.tlSearchPlaceholder}
              aria-label={s.tlSearchLabel}
              data-testid="tools-search"
              autoComplete="off"
            />
            {query && (
              <button type="button" className="btn" onClick={() => setQuery("")}>
                {s.tlSearchClear}
              </button>
            )}
          </div>
          <nav className={styles.jump} aria-label={s.tlJumpTo}>
            {visibleSections.map((sec) => (
              <a key={sec.id} href={`#tools-${sec.id}`}>
                {sec.title}
              </a>
            ))}
          </nav>
        </div>

        {nothing && <p className="muted" role="status">{s.tlNoMatch}</p>}

        {visibleSections.map((sec) => (
          <section key={sec.id} id={`tools-${sec.id}`} className={styles.section} aria-labelledby={`tools-${sec.id}-h`}>
            <h3 id={`tools-${sec.id}-h`}>{sec.title}</h3>
            <div className={styles.grid}>
              {sec.id === "deadlines" ? (
                <LimitationSection catalog={catalog} error={error} reload={reload} query={limToolMatch ? "" : query} haystacks={haystacks} />
              ) : (
                visibleTools.filter((tool) => tool.section === sec.id).map((tool) => tool.node)
              )}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
