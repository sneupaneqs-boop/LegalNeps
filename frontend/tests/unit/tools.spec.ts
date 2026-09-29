import { expect, test } from "@playwright/test";
import { bsIso, entryHaystack, formatBs, lawHref, LimitationEntry, matchesQuery, provisionsOf, searchForm } from "../../lib/tools";
import { toolsEn, toolsNe } from "../../lib/i18n-tools";

test("searchForm lower-cases, folds Nepali digits and collapses whitespace", () => {
  expect(searchForm("  Six   MONTHS ")).toBe("six months");
  expect(searchForm("६ महिना")).toBe("6 महिना");
  expect(searchForm("दफा २३५")).toBe("दफा 235");
});

test("matchesQuery needs every word, in any order", () => {
  const hay = searchForm("Bounced cheque complaint | 1 year | बैङ्किङ्ग कसूर | s. 17");
  expect(matchesQuery(hay, "cheque")).toBe(true);
  expect(matchesQuery(hay, "1 year cheque")).toBe(true);
  expect(matchesQuery(hay, "cheque 2 years")).toBe(false);
  expect(matchesQuery(hay, "  ")).toBe(true); // an empty query matches everything
  expect(matchesQuery(hay, "१ year")).toBe(true); // Nepali digit in the query
});

test("lawHref encodes the section (sub-sections have spaces and brackets)", () => {
  expect(lawHref({ slug: "abc123", section: "235" })).toBe("/law/abc123/235");
  expect(lawHref({ slug: "abc123", section: "50 (1)" })).toBe("/law/abc123/50%20(1)");
  expect(lawHref({ slug: "abc123", section: "169क" })).toBe(`/law/abc123/${encodeURIComponent("169क")}`);
  expect(lawHref({ slug: "abc123", section: null })).toBe("/law/abc123");
});

test("bsIso pads and rejects incomplete or non-integer input", () => {
  expect(bsIso("2081", "1", "5")).toBe("2081-01-05");
  expect(bsIso("2081", "", "5")).toBe("");
  expect(bsIso("20x1", "1", "5")).toBe("");
  expect(bsIso("2081", "1.5", "5")).toBe("");
});

test("formatBs names the month in both languages", () => {
  expect(formatBs({ year: 2082, month: 12, day: 30 }, "en")).toBe("30 Chaitra 2082");
  expect(formatBs({ year: 2081, month: 1, day: 1 }, "ne")).toBe("1 बैशाख 2081");
});

test("provisionsOf finds every distinct cited provision in a result", () => {
  const p = { law_title_ne: "श्रम ऐन, २०७४", section: "31", slug: "0dc3b2516057", citation: "श्रम ऐन, २०७४, दफा 31", url: null, status: null, note: {} };
  const q = { ...p, section: "30", citation: "श्रम ऐन, २०७४, दफा 30" };
  const result = { pay: 5, provisions: [p, q, p], nested: { provision: q } };
  const found = provisionsOf(result);
  expect(found.map((x) => x.section)).toEqual(["31", "30"]);
  expect(provisionsOf({ a: 1 })).toEqual([]);
});

test("entryHaystack covers names, keywords, law, section and category in both languages", () => {
  const entry = {
    id: "cheque_dishonour_complaint",
    category: "banking",
    name: { en: "Bounced cheque complaint", ne: "चेक अनादर भएको उजुरी" },
    period: { kind: "fixed", value: 1, unit: "years", text: { en: "1 year", ne: "१ वर्ष" } },
    start: { kind: "other", en: "the date the dishonour was certified", ne: "प्रमाणित भएको मितिदेखि" },
    applies_to: null,
    notes: null,
    long_stop: null,
    keywords: ["cheque", "चेक"],
    needs_review: false,
    computable: true,
    citation: { law_title_ne: "बैङ्किङ्ग कसूर तथा सजाय ऐन, २०६४", law_en: "Banking Offence and Punishment Act", section: "17", clause: "(१क)", slug: "s", citation: "c", url: null, resolved: true },
  } as unknown as LimitationEntry;
  const hay = entryHaystack(entry, { en: "Banking, cheques & finance", ne: "बैङ्किङ, चेक तथा वित्त" });
  for (const q of ["bounced", "चेक", "1 year", "banking offence", "17", "certified", "cheques"]) expect(matchesQuery(hay, q)).toBe(true);
  expect(matchesQuery(hay, "divorce")).toBe(false);
});

test("Nepali tools strings cover every English key and keep the same placeholders", () => {
  expect(Object.keys(toolsNe).sort()).toEqual(Object.keys(toolsEn).sort());
  for (const key of Object.keys(toolsEn) as (keyof typeof toolsEn)[]) {
    const en = toolsEn[key];
    const ne = toolsNe[key];
    expect(typeof ne).toBe(typeof en);
    if (typeof en === "function" && typeof ne === "function") {
      expect((ne as (...a: number[]) => string)(7, 9)).toContain("7");
      expect((en as (...a: number[]) => string)(7, 9)).toContain("7");
    } else {
      expect((ne as string).trim().length).toBeGreaterThan(0);
    }
  }
});
