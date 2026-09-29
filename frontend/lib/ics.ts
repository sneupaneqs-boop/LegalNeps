// Minimal RFC 5545 iCalendar generation for compliance deadlines (all-day events).

export type IcsEvent = {
  uid: string;
  /** AD date, YYYY-MM-DD */
  date: string;
  summary: string;
  description?: string;
  url?: string | null;
};

function escapeText(s: string): string {
  return s.replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\r?\n/g, "\\n");
}

// Lines must be at most 75 octets; continuation lines start with a space.
function fold(line: string): string {
  const enc = new TextEncoder();
  if (enc.encode(line).length <= 75) return line;
  const out: string[] = [];
  let cur = "";
  let curBytes = 0;
  let limit = 75;
  for (const ch of line) {
    const b = enc.encode(ch).length;
    if (curBytes + b > limit) {
      out.push(cur);
      cur = "";
      curBytes = 0;
      limit = 74; // the leading space counts
    }
    cur += ch;
    curBytes += b;
  }
  out.push(cur);
  return out.join("\r\n ");
}

function compact(date: string): string {
  return date.replace(/-/g, "");
}

function nextDay(date: string): string {
  const [y, m, d] = date.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d + 1));
  return `${dt.getUTCFullYear()}${String(dt.getUTCMonth() + 1).padStart(2, "0")}${String(dt.getUTCDate()).padStart(2, "0")}`;
}

function stamp(now: Date): string {
  return now.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "Z");
}

export function buildIcs(events: IcsEvent[], now: Date = new Date()): string {
  const lines: string[] = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Kanooni Sathi//Compliance Radar//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH"];
  for (const ev of events) {
    lines.push(
      "BEGIN:VEVENT",
      `UID:${ev.uid}@kanooni-sathi`,
      `DTSTAMP:${stamp(now)}`,
      `DTSTART;VALUE=DATE:${compact(ev.date)}`,
      `DTEND;VALUE=DATE:${nextDay(ev.date)}`,
      `SUMMARY:${escapeText(ev.summary)}`
    );
    if (ev.description) lines.push(`DESCRIPTION:${escapeText(ev.description)}`);
    if (ev.url) lines.push(`URL:${ev.url}`);
    // remind a week ahead and the day before
    for (const days of [7, 1]) {
      lines.push("BEGIN:VALARM", "ACTION:DISPLAY", `DESCRIPTION:${escapeText(ev.summary)}`, `TRIGGER:-P${days}D`, "END:VALARM");
    }
    lines.push("END:VEVENT");
  }
  lines.push("END:VCALENDAR");
  return lines.map(fold).join("\r\n") + "\r\n";
}
