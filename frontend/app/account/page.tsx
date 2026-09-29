"use client";

import { Session } from "@supabase/supabase-js";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ErrorBox, errorText, Loading, RequireAuth } from "@/components/ui";
import { listLlmUsage, LlmUsage } from "@/lib/api";
import { useLang } from "@/lib/LangContext";
import { fetchPlan } from "@/lib/plan";
import { signOut } from "@/lib/supabase";

export default function AccountPage() {
  const { t } = useLang();
  return (
    <div className="page">
      <div className="content">
        <h2>{t.accountTitle}</h2>
        <RequireAuth>{(session) => <Account session={session} />}</RequireAuth>
      </div>
    </div>
  );
}

function Account({ session }: { session: Session }) {
  const { lang, t } = useLang();
  const token = session.access_token;
  const [plan, setPlan] = useState<string | null>(null);
  const [usage, setUsage] = useState<LlmUsage[] | null>(null);
  const [error, setError] = useState<{ e: unknown } | null>(null);

  useEffect(() => {
    let alive = true;
    fetchPlan(session.user.id).then((p) => alive && setPlan(p));
    return () => {
      alive = false;
    };
  }, [session.user.id]);

  const loadUsage = useCallback(() => {
    setError(null);
    listLlmUsage(token)
      .then(setUsage)
      .catch((e) => setError({ e }));
  }, [token]);
  useEffect(loadUsage, [loadUsage]);

  const planLabel = plan === null ? "…" : plan === "free" ? t.planFree : plan.charAt(0).toUpperCase() + plan.slice(1);
  const total = usage?.reduce((sum, u) => sum + (u.cost_usd || 0), 0) ?? 0;

  return (
    <>
      <section className="card">
        <dl className="kv">
          <dt>{t.accountEmail}</dt>
          <dd data-testid="account-email">{session.user.email}</dd>
          <dt>{t.accountPlan}</dt>
          <dd>
            <span className="pill ok">{planLabel}</span> <span className="muted">· {t.planUpgradeSoon}</span>
          </dd>
        </dl>
        <div className="row" style={{ marginTop: 12 }}>
          <Link className="btn btn-small" href="/saved">
            {t.navSaved}
          </Link>
          <button className="btn btn-small" onClick={() => signOut()}>
            {t.signOut}
          </button>
        </div>
      </section>

      <section>
        <h3>{t.accountUsageHeading}</h3>
        {error && <ErrorBox message={errorText(error.e, t)} onRetry={loadUsage} />}
        {!error && usage === null && <Loading />}
        {usage && usage.length === 0 && (
          <div className="notice">{plan === "free" || plan === null ? t.accountUsageFreeNote : t.accountUsageEmpty}</div>
        )}
        {usage && usage.length > 0 && (
          <>
            <div className="row row-between" style={{ marginBottom: 8 }}>
              <strong>
                {t.usageTotal}: ${total.toFixed(4)}
              </strong>
            </div>
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>{t.usageWhen}</th>
                    <th>{t.usageEndpoint}</th>
                    <th>{t.usageModel}</th>
                    <th>{t.usageTokens}</th>
                    <th>{t.usageCost}</th>
                  </tr>
                </thead>
                <tbody>
                  {usage.map((u) => (
                    <tr key={u.id}>
                      <td>{new Date(u.created_at).toLocaleString(lang === "ne" ? "ne-NP" : "en-GB")}</td>
                      <td>{u.endpoint.replace(/^\/api\//, "")}</td>
                      <td>{u.model ?? u.tier}</td>
                      <td>
                        {u.input_tokens ?? "–"} / {u.output_tokens ?? "–"}
                      </td>
                      <td>${u.cost_usd.toFixed(4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </section>
    </>
  );
}
