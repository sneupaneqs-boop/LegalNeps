import { supabase } from "./supabase";

// The API has no "who am I / which plan" endpoint, so read the caller's own
// profiles row straight from Supabase (row-level security limits it to them).
// Best effort: anything unexpected resolves to "free", the same default the
// backend uses (supa.profile_get_plan).
export async function fetchPlan(userId: string): Promise<string> {
  if (!supabase) return "free";
  try {
    const { data, error } = await supabase.from("profiles").select("plan").eq("id", userId).maybeSingle();
    if (error || !data || typeof data.plan !== "string" || !data.plan) return "free";
    return data.plan;
  } catch {
    return "free";
  }
}
