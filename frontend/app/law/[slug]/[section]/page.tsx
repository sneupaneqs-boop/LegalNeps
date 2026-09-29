import Link from "next/link";
import { notFound } from "next/navigation";
import { getLawSection } from "@/lib/api";
import { strings } from "@/lib/i18n";

const t = strings.en;

export default async function LawSectionPage({
  params,
}: {
  params: Promise<{ slug: string; section: string }>;
}) {
  const { slug, section: rawSection } = await params;
  // Next passes dynamic segments still percent-encoded ("517%20(1)");
  // getLawSection encodes again, so decode first or sub-sections 404.
  const section = decodeURIComponent(rawSection);
  const s = await getLawSection(slug, section);
  if (!s) notFound();

  return (
    <div className="page law-page">
      <div className="law-body">
        <Link className="back-link" href={`/law/${slug}`}>
          ← {s.doc_title_ne || t.backToDoc}
        </Link>

        {s.status === "bill" && <div className="warning-banner">{t.billWarning}</div>}

        <h2 className="law-title">{s.title_ne}</h2>
        {s.title_en && <div className="law-title-en">{s.title_en}</div>}
        <div className="section-citation">{s.source_ne}</div>

        <div className="section-text">{s.text_ne}</div>
        {s.text_en && (
          <>
            <div className="section-text-en-label">English translation</div>
            <div className="section-text section-text-en">{s.text_en}</div>
          </>
        )}

        {s.url && (
          <a className="src-link official-link" href={s.url} target="_blank" rel="noopener noreferrer">
            {t.officialPdf} ↗
          </a>
        )}

        <div className="section-nav">
          {s.prev ? (
            <Link className="section-nav-link" href={`/law/${slug}/${encodeURIComponent(s.prev.section || "")}`}>
              ← {t.prevSection}
            </Link>
          ) : (
            <span />
          )}
          {s.next ? (
            <Link className="section-nav-link" href={`/law/${slug}/${encodeURIComponent(s.next.section || "")}`}>
              {t.nextSection} →
            </Link>
          ) : (
            <span />
          )}
        </div>
      </div>
    </div>
  );
}
