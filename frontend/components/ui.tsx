"use client";

import { Session } from "@supabase/supabase-js";
import AuthWidget from "@/components/AuthWidget";
import { ApiError, ResolvedProvision } from "@/lib/api";
import { strings } from "@/lib/i18n";
import { useLang } from "@/lib/LangContext";
import { authAvailable } from "@/lib/supabase";
import { useAuth } from "@/lib/useAuth";

export type T = (typeof strings)["en"];

/** Human-readable text for a failed API call, in the current language. */
export function errorText(e: unknown, t: T): string {
  if (e instanceof ApiError) {
    if (e.status === 0) return t.errorNetwork;
    if (e.status === 401) return t.sessionExpired;
    if (e.status === 429) return t.errorRateLimit;
    if (e.status === 503) return t.errorUnavailable;
    // 4xx validation messages from the server are short and useful (e.g. "'x' is required")
    if (e.status >= 400 && e.status < 500 && e.detail) return `${t.errorGeneric} (${e.detail})`;
  }
  return t.errorGeneric;
}

export function ErrorBox({ message, onRetry }: { message: string; onRetry?: () => void }) {
  const { t } = useLang();
  return (
    <div className="notice error" role="alert">
      <div>{message}</div>
      {onRetry && (
        <button className="btn btn-small" style={{ marginTop: 8 }} onClick={onRetry}>
          {t.retry}
        </button>
      )}
    </div>
  );
}

export function Loading() {
  const { t } = useLang();
  return (
    <div className="muted" role="status">
      {t.loading}
    </div>
  );
}

/** Sign-in prompt shown in place of a page's content when signed out. */
export function SignInPrompt({ body }: { body?: string }) {
  const { lang, t } = useLang();
  return (
    <div className="card signin-card" data-testid="signin-prompt">
      <h2>{t.signInRequired}</h2>
      <p className="lede">{body ?? t.signInRequiredBody}</p>
      {authAvailable() ? <AuthWidget lang={lang} /> : <p className="muted">{t.authUnavailable}</p>}
    </div>
  );
}

/**
 * Renders `children(session)` for a signed-in user; a loading line while the
 * session is restored; a sign-in prompt when signed out.
 */
export function RequireAuth({
  children,
  body,
}: {
  children: (session: Session) => React.ReactNode;
  body?: string;
}) {
  const { session, loading } = useAuth();
  if (loading) return <Loading />;
  if (!session) return <SignInPrompt body={body} />;
  return <>{children(session)}</>;
}

/** A cited provision, with a link to the official source when there is one. */
export function Provision({ p, lang }: { p: ResolvedProvision; lang: "en" | "ne" }) {
  const { t } = useLang();
  const note = p.note?.[lang] || p.note?.en || p.note?.ne;
  return (
    <div className="provision">
      <span>{p.citation}</span>
      {p.url && (
        <>
          {" · "}
          <a href={p.url} target="_blank" rel="noopener noreferrer">
            {t.officialSourceLink}
          </a>
        </>
      )}
      {note && <div>{note}</div>}
    </div>
  );
}

export function formatDate(iso: string, lang: "en" | "ne"): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString(lang === "ne" ? "ne-NP" : "en-GB", { year: "numeric", month: "short", day: "numeric" });
}

export function formatNpr(n: number): string {
  return `Rs. ${n.toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;
}
