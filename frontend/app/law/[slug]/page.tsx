import Link from "next/link";
import { notFound } from "next/navigation";
import { getLawDoc } from "@/lib/api";
import { strings } from "@/lib/i18n";

const t = strings.en;

const DOC_TYPE_LABEL: Record<string, string> = {
  act: t.docTypeAct, rule: t.docTypeRule, constitution: t.docTypeConstitution,
  order: t.docTypeOrder, directive: t.docTypeDirective, treaty: t.docTypeTreaty, other: t.docTypeOther,
};

export default async function LawDocPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const doc = await getLawDoc(slug);
  if (!doc) notFound();

  return (
    <div className="page law-page">
      <div className="law-body">
        <h2 className="law-title">{doc.doc_title_ne}</h2>
        {doc.doc_title_en && <div className="law-title-en">{doc.doc_title_en}</div>}

        <div className="law-meta">
          {doc.doc_type && <span className="badge law">{DOC_TYPE_LABEL[doc.doc_type] || doc.doc_type}</span>}
          {doc.status === "in_force" && <span className="status-pill in-force">{t.statusInForce}</span>}
          {doc.status === "bill" && <span className="status-pill bill">{t.statusBill}</span>}
          {doc.status === "unknown" && <span className="status-pill unknown">{t.statusUnknown}</span>}
        </div>

        {doc.status === "bill" && <div className="warning-banner">{t.billWarning}</div>}
        {doc.status === "unknown" && <div className="notice-banner">{t.unknownStatusNote}</div>}

        {doc.enacted_bs && (
          <div className="law-dates">
            <span>{t.enactedLabel}: {doc.enacted_bs} BS</span>
            {doc.amended_by.length > 0 && (
              <span> · {t.amendedLabel}: {doc.amended_by.length}</span>
            )}
          </div>
        )}
        {doc.amended_by.length > 0 && (
          <ul className="amendment-list">
            {doc.amended_by.map((a, i) => (
              <li key={i}>
                {a.name} — {a.date_bs} BS
              </li>
            ))}
          </ul>
        )}

        {doc.url && (
          <a className="src-link official-link" href={doc.url} target="_blank" rel="noopener noreferrer">
            {t.officialPdf} ↗
          </a>
        )}

        <div className="section-list">
          {doc.sections.map((s) => (
            <Link
              key={s.id}
              className="section-item"
              href={s.section ? `/law/${slug}/${encodeURIComponent(s.section)}` : `/law/${slug}`}
            >
              <div className="section-item-title">
                {s.section && <span className="section-num">{s.section}</span>}
                {s.title_ne}
              </div>
              <div className="section-item-snippet">{s.snippet}</div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
