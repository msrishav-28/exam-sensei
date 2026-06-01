import { createClient } from "@supabase/supabase-js";

const url = (import.meta.env.VITE_SUPABASE_URL as string | undefined) ?? "";
const anonKey = (import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined) ?? "";

export const isSupabaseConfigured = Boolean(url && anonKey);

if (!isSupabaseConfigured) {
  // The landing page works without Supabase; only auth + product screens need it.
  // Warn loudly in dev so a missing .env is obvious.
  if (import.meta.env.DEV) {
    console.warn(
      "[supabase] VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY are not set — " +
        "login, signup and the product app will not work until they are.",
    );
  }
}

// supabase-js validates the URL eagerly inside createClient(), so we can't
// pass an empty string. When envs aren't configured we hand it a clearly
// unreachable placeholder — the client constructs cleanly (landing + SSR
// don't crash), and any actual auth call surfaces a normal network error
// that the form handlers already toast.
const PLACEHOLDER_URL = "https://not-configured.supabase.co";
const PLACEHOLDER_KEY = "anon-key-placeholder";

/**
 * Browser Supabase client. supabase-js guards storage access for SSR
 * (no window → in-memory fallback), so this is safe to import on the server;
 * a real session is only ever read on the client.
 */
export const supabase = createClient(
  url || PLACEHOLDER_URL,
  anonKey || PLACEHOLDER_KEY,
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
  },
);
