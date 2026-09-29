"use client";

import { useCallback, useEffect, useState } from "react";
import { ErrorBox, errorText, Loading, RequireAuth } from "@/components/ui";
import {
  ApiError,
  CompanyProfile,
  EntityType,
  getCompanyProfile,
  listUpcomingObligations,
  ObligationDue,
  saveCompanyProfile,
} from "@/lib/api";
import { saveBlob } from "@/lib/download";
import { buildIcs } from "@/lib/ics";
import { useLang } from "@/lib/LangContext";

export default function CompliancePage() {
  const { t } = useLang();
  return (
    <div className="page">
      <div className="content">
        <h2>{t.complianceTitle}</h2>
        <p className="lede">{t.complianceIntro}</p>
        <RequireAuth>{(session) => <Compliance token={session.access_token} />}</RequireAuth>
      </div>
    </div>
  );
}

const ENTITY_TYPES: EntityType[] = ["private_limited", "public_limited", "partnership", "sole_proprietorship"];
const WINDOWS = [30, 60, 90, 180, 365];

function Compliance({ token }: { token: string }) {
  // profile === undefined: still loading; null: none saved yet
  const [profile, setProfile] = useState<CompanyProfile | null | undefined>(undefined);
  const [error, setError] = useState<{ e: unknown } | null>(null);

  const load = useCallback(() => {
    setError(null);
    getCompanyProfile(token)
      .then(setProfile)
      .catch((e) => setError({ e }));
  }, [token]);
  useEffect(load, [load]);

  const { t } = useLang();
  if (error) return <ErrorBox message={errorText(error.e, t)} onRetry={load} />;
  if (profile === undefined) return <Loading />;

  return (
    <>
      <ProfileForm token={token} profile={profile} onSaved={setProfile} />
      <Obligations token={token} hasProfile={profile !== null} version={profile?.updated_at ?? ""} />
    </>
  );
}

function ProfileForm({ token, profile, onSaved }: { token: string; profile: CompanyProfile | null; onSaved: (p: CompanyProfile) => void }) {
  const { t } = useLang();
  const [name, setName] = useState(profile?.company_name ?? "");
  const [entity, setEntity] = useState<EntityType>((profile?.entity_type as EntityType) ?? "private_limited");
  const [pan, setPan] = useState(profile?.pan_vat_registered ?? false);
  const [emp, setEmp] = useState(profile?.has_employees ?? false);
  const [email, setEmail] = useState(profile?.reminder_email ?? "");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ kind: "success" | "error"; text: string } | null>(null);

  const entityLabel: Record<EntityType, string> = {
    private_limited: t.entityPrivateLimited,
    public_limited: t.entityPublicLimited,
    partnership: t.entityPartnership,
    sole_proprietorship: t.entitySoleProprietorship,
  };

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setBusy(true);
    setMsg(null);
    try {
      const saved = await saveCompanyProfile(token, {
        company_name: name.trim(),
        entity_type: entity,
        pan_vat_registered: pan,
        has_employees: emp,
        reminder_email: email.trim() || null,
      });
      onSaved(saved);
      setMsg({ kind: "success", text: t.profileSaved });
    } catch (err) {
      setMsg({ kind: "error", text: errorText(err, t) });
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="card form" onSubmit={submit}>
      <h3>{t.profileHeading}</h3>
      <div className="field">
        <label htmlFor="cp-name">{t.profileCompanyName}</label>
        <input id="cp-name" className="input" value={name} maxLength={200} onChange={(e) => setName(e.target.value)} required />
      </div>
      <div className="field">
        <label htmlFor="cp-entity">{t.profileEntityType}</label>
        <select id="cp-entity" className="select" value={entity} onChange={(e) => setEntity(e.target.value as EntityType)}>
          {ENTITY_TYPES.map((k) => (
            <option key={k} value={k}>
              {entityLabel[k]}
            </option>
          ))}
        </select>
      </div>
      <label className="check">
        <input type="checkbox" checked={pan} onChange={(e) => setPan(e.target.checked)} />
        {t.profilePanVat}
      </label>
      <label className="check">
        <input type="checkbox" checked={emp} onChange={(e) => setEmp(e.target.checked)} />
        {t.profileHasEmployees}
      </label>
      <div className="field">
        <label htmlFor="cp-email">{t.profileReminderEmail}</label>
        <input id="cp-email" className="input" type="email" value={email} maxLength={320} onChange={(e) => setEmail(e.target.value)} />
      </div>
      {msg && (
        <div className={`notice ${msg.kind}`} role={msg.kind === "error" ? "alert" : "status"}>
          {msg.text}
        </div>
      )}
      <div>
        <button className="btn btn-primary" type="submit" disabled={busy || !name.trim()}>
          {busy ? t.saving : t.profileSave}
        </button>
      </div>
    </form>
  );
}

function daysLabel(days: number, t: ReturnType<typeof useLang>["t"]): { text: string; cls: string } {
  if (days < 0) return { text: `${-days} ${t.overdueBy}`, cls: "bad" };
  if (days === 0) return { text: t.dueToday, cls: "bad" };
  return { text: `${days} ${t.daysRemaining}`, cls: days <= 14 ? "warn" : "ok" };
}

function Obligations({ token, hasProfile, version }: { token: string; hasProfile: boolean; version: string }) {
  const { lang, t } = useLang();
  const [within, setWithin] = useState(90);
  const [items, setItems] = useState<ObligationDue[] | null>(null);
  const [error, setError] = useState<{ e: unknown } | null>(null);

  const load = useCallback(() => {
    if (!hasProfile) {
      setItems(null);
      return;
    }
    setError(null);
    setItems(null);
    listUpcomingObligations(token, within)
      .then((r) => setItems(r.obligations))
      .catch((e) => {
        // no profile on the server yet -> same as "needs profile"
        if (e instanceof ApiError && e.status === 404) setItems(null);
        else setError({ e });
      });
  }, [token, within, hasProfile]);
  // reload when the window changes or the profile is (re)saved
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(load, [load, version]);

  function addToCalendar() {
    if (!items || items.length === 0) return;
    const ics = buildIcs(
      items.map((o) => ({
        uid: `${o.id}-${o.due_date_ad}`,
        date: o.due_date_ad,
        summary: o[lang === "ne" ? "title_ne" : "title_en"],
        description: `${o.citation}\n${t.dueBs}: ${o.due_date_bs}\n${t.period}: ${o.period}`,
        url: o.source_url,
      }))
    );
    saveBlob(new Blob([ics], { type: "text/calendar;charset=utf-8" }), "kanooni-sathi-deadlines.ics");
  }

  return (
    <section>
      <div className="row row-between" style={{ marginBottom: 10 }}>
        <h3 style={{ margin: 0 }}>{t.obligationsHeading}</h3>
        {hasProfile && (
          <label className="row muted" style={{ gap: 6 }}>
            {t.obligationsWithin}
            <select className="select" style={{ width: "auto", padding: "4px 8px" }} value={within} onChange={(e) => setWithin(Number(e.target.value))}>
              {WINDOWS.map((w) => (
                <option key={w} value={w}>
                  {w}
                </option>
              ))}
            </select>
            {t.obligationsDays}
          </label>
        )}
      </div>

      {!hasProfile && <div className="notice">{t.obligationsNeedProfile}</div>}
      {hasProfile && error && <ErrorBox message={errorText(error.e, t)} onRetry={load} />}
      {hasProfile && !error && items === null && <Loading />}
      {items && items.length === 0 && <div className="notice">{t.obligationsEmpty}</div>}
      {items && items.length > 0 && (
        <>
          <div className="row" style={{ marginBottom: 10 }}>
            <button className="btn" onClick={addToCalendar} data-testid="add-to-calendar">
              📅 {t.addToCalendar}
            </button>
            <span className="muted">{t.calendarNote}</span>
          </div>
          <ul className="list" data-testid="obligation-list">
            {items.map((o) => {
              const d = daysLabel(o.days_remaining, t);
              return (
                <li className="card" key={`${o.id}-${o.due_date_ad}`}>
                  <div className="row row-between" style={{ alignItems: "flex-start" }}>
                    <div className="card-title">{lang === "ne" ? o.title_ne : o.title_en}</div>
                    <span className={`pill ${d.cls}`}>{d.text}</span>
                  </div>
                  <dl className="kv" style={{ marginTop: 8 }}>
                    <dt>{t.dueBs}</dt>
                    <dd>{o.due_date_bs}</dd>
                    <dt>{t.dueAd}</dt>
                    <dd>{o.due_date_ad}</dd>
                    <dt>{t.period}</dt>
                    <dd>{o.period}</dd>
                    <dt>{t.citation}</dt>
                    <dd>
                      {o.citation}
                      {o.source_url && (
                        <>
                          {" · "}
                          <a href={o.source_url} target="_blank" rel="noopener noreferrer" style={{ color: "var(--accent-2)" }}>
                            {t.officialSourceLink}
                          </a>
                        </>
                      )}
                    </dd>
                  </dl>
                </li>
              );
            })}
          </ul>
        </>
      )}
    </section>
  );
}
