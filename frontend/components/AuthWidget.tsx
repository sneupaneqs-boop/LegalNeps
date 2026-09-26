"use client";

import { useState } from "react";
import { authAvailable, sendOtp, signOut, verifyOtp } from "@/lib/supabase";
import { useAuth } from "@/lib/useAuth";
import { Lang, strings } from "@/lib/i18n";

export default function AuthWidget({ lang }: { lang: Lang }) {
  const t = strings[lang];
  const { session, loading } = useAuth();
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState<"email" | "code">("email");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!authAvailable()) return null;
  if (loading) return null;

  if (session) {
    return (
      <div className="auth-widget">
        <span className="auth-email" title={session.user.email}>
          {session.user.email}
        </span>
        <button className="auth-signout" onClick={() => signOut()}>
          {t.signOut}
        </button>
      </div>
    );
  }

  async function handleSendCode(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim()) return;
    setBusy(true);
    setError(null);
    const { error } = await sendOtp(email.trim());
    setBusy(false);
    if (error) setError(error);
    else setStep("code");
  }

  async function handleVerify(e: React.FormEvent) {
    e.preventDefault();
    if (!code.trim()) return;
    setBusy(true);
    setError(null);
    const { error } = await verifyOtp(email.trim(), code.trim());
    setBusy(false);
    if (error) setError(error);
    else {
      setOpen(false);
      setStep("email");
      setEmail("");
      setCode("");
    }
  }

  return (
    <div className="auth-widget">
      <button className="nav-link" onClick={() => setOpen((o) => !o)}>
        {t.signIn}
      </button>
      {open && (
        <div className="auth-popover">
          {step === "email" ? (
            <form onSubmit={handleSendCode}>
              <input
                type="email"
                required
                placeholder={t.emailPlaceholder}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <button type="submit" disabled={busy}>
                {t.sendCode}
              </button>
            </form>
          ) : (
            <form onSubmit={handleVerify}>
              <p className="auth-hint">{t.codeSentTo} {email}</p>
              <input
                inputMode="numeric"
                required
                placeholder={t.codePlaceholder}
                value={code}
                onChange={(e) => setCode(e.target.value)}
              />
              <button type="submit" disabled={busy}>
                {t.verifyCode}
              </button>
            </form>
          )}
          {error && <p className="auth-error">{error}</p>}
        </div>
      )}
    </div>
  );
}
