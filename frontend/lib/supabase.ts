import { createClient, Session } from "@supabase/supabase-js";

const url = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

// null when not configured (e.g. local dev without a Supabase project) -
// callers must handle that instead of crashing, so the rest of the app
// (chat, search, law browser) keeps working without an account system.
export const supabase = url && anonKey ? createClient(url, anonKey) : null;

export function authAvailable(): boolean {
  return supabase !== null;
}

export async function sendOtp(email: string): Promise<{ error: string | null }> {
  if (!supabase) return { error: "auth not configured" };
  const { error } = await supabase.auth.signInWithOtp({ email });
  return { error: error?.message || null };
}

export async function verifyOtp(email: string, token: string): Promise<{ error: string | null }> {
  if (!supabase) return { error: "auth not configured" };
  const { error } = await supabase.auth.verifyOtp({ email, token, type: "email" });
  return { error: error?.message || null };
}

export async function signOut(): Promise<void> {
  await supabase?.auth.signOut();
}

export async function getSession(): Promise<Session | null> {
  if (!supabase) return null;
  const { data } = await supabase.auth.getSession();
  return data.session;
}

export function onAuthChange(cb: (session: Session | null) => void): () => void {
  if (!supabase) return () => {};
  const { data } = supabase.auth.onAuthStateChange((_event, session) => cb(session));
  return () => data.subscription.unsubscribe();
}
