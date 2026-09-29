"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import AuthWidget from "@/components/AuthWidget";
import { useLang } from "@/lib/LangContext";
import { useAuth } from "@/lib/useAuth";

const NAV = [
  { href: "/", key: "navAsk" },
  { href: "/search", key: "navSearchShort" },
  { href: "/action-plans", key: "navPlans" },
  { href: "/draft", key: "navDraft" },
  { href: "/audit", key: "navAudit" },
  { href: "/matters", key: "navMatters" },
  { href: "/tools", key: "navTools" },
  { href: "/compliance", key: "navCompliance" },
] as const;

function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(href + "/");
}

// Header shown on every page: brand, primary navigation (collapses to a menu
// on phones), sign-in widget, Account link when signed in, language toggle.
export default function Shell({ children }: { children: React.ReactNode }) {
  const { lang, setLang, t } = useLang();
  const { session } = useAuth();
  const pathname = usePathname() || "/";
  const [open, setOpen] = useState(false);

  // close the phone menu after navigating
  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  const items: { href: string; label: string }[] = NAV.map((n) => ({ href: n.href, label: t[n.key] }));
  if (session) items.push({ href: "/account", label: t.navAccount });

  return (
    <>
      <header className="site-header">
        <div className="site-header-inner">
          <Link className="site-brand" href="/">
            {t.appName}
          </Link>

          <nav id="site-nav" className={`site-nav${open ? " open" : ""}`} aria-label={t.navMain}>
            {items.map((it) => (
              <Link
                key={it.href}
                href={it.href}
                className={`site-nav-link${isActive(pathname, it.href) ? " active" : ""}`}
                aria-current={isActive(pathname, it.href) ? "page" : undefined}
              >
                {it.label}
              </Link>
            ))}
            <div className="site-nav-auth">
              <AuthWidget lang={lang} />
            </div>
          </nav>

          <button className="lang-toggle site-lang" onClick={() => setLang(lang === "en" ? "ne" : "en")}>
            {t.langToggle}
          </button>
          <button
            className="site-burger"
            aria-expanded={open}
            aria-controls="site-nav"
            aria-label={open ? t.navMenuClose : t.navMenu}
            onClick={() => setOpen((o) => !o)}
          >
            <span aria-hidden="true">{open ? "✕" : "☰"}</span>
          </button>
        </div>
      </header>
      {children}
    </>
  );
}
