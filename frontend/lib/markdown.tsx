import { Fragment, ReactNode } from "react";

// Minimal, XSS-safe renderer for the subset of Markdown the model produces
// (headings, bullets, numbered lists, **bold**, *italic*) plus citation
// markers like [2] / [२] that link to the numbered source cards.

const DEV_DIGITS: Record<string, string> = {
  "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
  "५": "5", "६": "6", "७": "7", "८": "8", "९": "9",
};
const toAscii = (s: string) => s.replace(/[०-९]/g, (d) => DEV_DIGITS[d]);

function inline(text: string, msgId: string, maxN: number): ReactNode[] {
  const out: ReactNode[] = [];
  const re = /(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|\[[0-9०-९]{1,2}\])/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let k = 0;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(text.slice(last, m.index));
    const tok = m[0];
    if (tok.startsWith("**")) {
      out.push(<strong key={k++}>{tok.slice(2, -2)}</strong>);
    } else if (tok.startsWith("[")) {
      const n = parseInt(toAscii(tok.slice(1, -1)), 10);
      if (n >= 1 && n <= maxN) {
        out.push(
          <a key={k++} className="cite" href={`#src-${msgId}-${n}`}>
            {n}
          </a>
        );
      } else {
        out.push(tok);
      }
    } else {
      out.push(<em key={k++}>{tok.slice(1, -1)}</em>);
    }
    last = m.index + tok.length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

export function renderAnswer(text: string, msgId: string, maxN: number): ReactNode {
  const lines = text.split("\n");
  const blocks: ReactNode[] = [];
  let list: { ordered: boolean; items: ReactNode[] } | null = null;
  const flush = () => {
    if (!list) return;
    const Tag = list.ordered ? "ol" : "ul";
    blocks.push(<Tag key={blocks.length}>{list.items}</Tag>);
    list = null;
  };

  lines.forEach((raw, i) => {
    const line = raw.trimEnd();
    const bullet = line.match(/^\s*[*\-•]\s+(.*)$/);
    const numbered = line.match(/^\s*(?:[0-9]+|[०-९]+)[.)]\s+(.*)$/);
    const heading = line.match(/^#{1,4}\s+(.*)$/);
    if (bullet || numbered) {
      const ordered = !!numbered && !bullet;
      if (!list || list.ordered !== ordered) {
        flush();
        list = { ordered, items: [] };
      }
      const body = (bullet ? bullet[1] : numbered![1]) as string;
      list.items.push(<li key={i}>{inline(body, msgId, maxN)}</li>);
      return;
    }
    flush();
    if (heading) {
      blocks.push(<h4 key={i}>{inline(heading[1], msgId, maxN)}</h4>);
    } else if (line.trim() === "") {
      blocks.push(<Fragment key={i} />);
    } else {
      blocks.push(<p key={i}>{inline(line, msgId, maxN)}</p>);
    }
  });
  flush();
  return blocks;
}
