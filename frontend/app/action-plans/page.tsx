import Link from "next/link";
import { listPlaybooks } from "@/lib/api";
import { strings } from "@/lib/i18n";

const t = strings.en;

const AREA_LABEL: Record<string, string> = {
  employment: t.areaEmployment, tenancy: t.areaTenancy, family: t.areaFamily,
  finance: t.areaFinance, consumer: t.areaConsumer, cyber: t.areaCyber,
};

export default async function ActionPlansPage() {
  const playbooks = await listPlaybooks();

  return (
    <div className="page law-page">
      <div className="law-body">
        <h2 className="law-title">{t.playbooksTitle}</h2>
        {playbooks.length === 0 && <div className="empty-state">{t.playbooksEmpty}</div>}
        <div className="section-list">
          {playbooks.map((p) => (
            <Link key={p.id} className="section-item playbook-card" href={`/action-plans/${p.id}`}>
              <div className="section-item-title">
                {p.area && <span className="section-num">{AREA_LABEL[p.area] || p.area}</span>}
                {p.issue.en}
              </div>
              <div className="section-item-snippet">{p.issue.ne}</div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
