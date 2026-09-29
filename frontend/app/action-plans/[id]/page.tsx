import Link from "next/link";
import { notFound } from "next/navigation";
import { Bilingual, getPlaybook, ResolvedProvision } from "@/lib/api";
import { strings } from "@/lib/i18n";

const t = strings.en;

function Bi({ b }: { b: Bilingual }) {
  return (
    <div className="bilingual-item">
      <div>{b.en}</div>
      <div className="bilingual-ne">{b.ne}</div>
    </div>
  );
}

function ProvisionCard({ p }: { p: ResolvedProvision }) {
  return (
    <div className="provision-card">
      <div className="provision-top">
        <Link className="src-link" href={p.section ? `/law/${p.slug}/${encodeURIComponent(p.section)}` : `/law/${p.slug}`}>
          {p.citation}
        </Link>
        {p.status === "bill" && <span className="badge bill">draft bill</span>}
      </div>
      {p.note?.en && <div className="provision-note">{p.note.en}</div>}
      {p.note?.ne && <div className="provision-note provision-note-ne">{p.note.ne}</div>}
    </div>
  );
}

export default async function ActionPlanPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const pb = await getPlaybook(id);
  if (!pb) notFound();

  return (
    <div className="page law-page">
      <div className="law-body">
        <Link className="back-link" href="/action-plans">
          {t.backToPlaybooks}
        </Link>

        <h2 className="law-title">{pb.issue.en}</h2>
        <div className="law-title-en">{pb.issue.ne}</div>

        <section className="playbook-section">
          <h3>{t.factQuestionsLabel}</h3>
          {pb.fact_questions.map((q, i) => (
            <Bi key={i} b={q} />
          ))}
        </section>

        <section className="playbook-section">
          <h3>{t.provisionsLabel}</h3>
          {pb.provisions.map((p, i) => (
            <ProvisionCard key={i} p={p} />
          ))}
        </section>

        <section className="playbook-section">
          <h3>{t.evidenceLabel}</h3>
          {pb.evidence.map((e, i) => (
            <Bi key={i} b={e} />
          ))}
        </section>

        <section className="playbook-section">
          <h3>{t.forumLabel}</h3>
          <Bi b={pb.forum} />
        </section>

        <section className="playbook-section">
          <h3>{t.limitationLabel}</h3>
          <Bi b={pb.limitation.note} />
          {pb.limitation.provision && <ProvisionCard p={pb.limitation.provision} />}
        </section>

        <section className="playbook-section">
          <h3>{t.nextStepsLabel}</h3>
          <ol className="next-steps-list">
            {pb.next_steps.map((s, i) => (
              <li key={i}>
                <Bi b={s} />
              </li>
            ))}
          </ol>
        </section>
      </div>
    </div>
  );
}
