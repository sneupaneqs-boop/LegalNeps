"use client";

import { Session } from "@supabase/supabase-js";
import { useEffect, useState } from "react";
import { getSession, onAuthChange } from "./supabase";

export function useAuth() {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    getSession().then((s) => {
      if (mounted) {
        setSession(s);
        setLoading(false);
      }
    });
    const unsubscribe = onAuthChange((s) => setSession(s));
    return () => {
      mounted = false;
      unsubscribe();
    };
  }, []);

  return { session, loading, user: session?.user ?? null };
}
