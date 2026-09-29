"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { Lang, strings } from "./i18n";

type LangCtx = { lang: Lang; setLang: (l: Lang) => void; t: (typeof strings)["en"] };

const STORAGE_KEY = "ks-lang";

const Ctx = createContext<LangCtx>({ lang: "en", setLang: () => {}, t: strings.en });

// Language is shared by every page (and persisted per browser) so the header
// toggle, the page content and the AuthWidget always agree.
export function LangProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>("en");

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(STORAGE_KEY);
      if (saved === "en" || saved === "ne") setLangState(saved);
    } catch {
      // storage blocked: stay on the default
    }
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    try {
      window.localStorage.setItem(STORAGE_KEY, l);
    } catch {
      // ignore
    }
  }, []);

  const value = useMemo(() => ({ lang, setLang, t: strings[lang] }), [lang, setLang]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useLang(): LangCtx {
  return useContext(Ctx);
}
