import { expect, test } from "@playwright/test";
import { buildIcs } from "../../lib/ics";

const NOW = new Date("2026-09-29T10:00:00Z");

test("buildIcs writes a valid all-day event with CRLF endings", () => {
  const ics = buildIcs(
    [{ uid: "vat-2026-10-25", date: "2026-10-25", summary: "VAT return, monthly", description: "Line1\nLine2; x", url: "https://example.org/a" }],
    NOW
  );
  expect(ics.startsWith("BEGIN:VCALENDAR\r\nVERSION:2.0\r\n")).toBe(true);
  expect(ics.endsWith("END:VCALENDAR\r\n")).toBe(true);
  expect(ics).toContain("UID:vat-2026-10-25@kanooni-sathi\r\n");
  expect(ics).toContain("DTSTAMP:20260929T100000Z\r\n");
  expect(ics).toContain("DTSTART;VALUE=DATE:20261025\r\n");
  expect(ics).toContain("DTEND;VALUE=DATE:20261026\r\n");
  // commas, semicolons and newlines are escaped
  expect(ics).toContain("SUMMARY:VAT return\\, monthly\r\n");
  expect(ics).toContain("DESCRIPTION:Line1\\nLine2\\; x\r\n");
  expect(ics.split("BEGIN:VEVENT").length - 1).toBe(1);
});

test("buildIcs rolls the end date over month and year boundaries", () => {
  const ics = buildIcs([{ uid: "a", date: "2026-12-31", summary: "Year end" }], NOW);
  expect(ics).toContain("DTEND;VALUE=DATE:20270101\r\n");
});

test("buildIcs folds long lines at 75 octets", () => {
  const ics = buildIcs([{ uid: "a", date: "2026-01-01", summary: "x".repeat(200) }], NOW);
  for (const line of ics.split("\r\n")) expect(new TextEncoder().encode(line).length).toBeLessThanOrEqual(75);
});

test("buildIcs handles Nepali text without splitting a character", () => {
  const summary = "मूल्य अभिवृद्धि कर विवरण दाखिला ".repeat(6);
  const ics = buildIcs([{ uid: "a", date: "2026-01-01", summary }], NOW);
  const unfolded = ics.replace(/\r\n /g, "");
  expect(unfolded).toContain(`SUMMARY:${summary}`);
});
