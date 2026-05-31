import { createClient } from "@supabase/supabase-js";

const url = (import.meta.env.VITE_SUPABASE_URL as string | undefined) ?? "";
const anonKey = (import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined) ?? "";

if (!url || !anonKey) {
  // The landing page works without Supabase; only auth + product screens need it.
  // Warn loudly in dev so a missing .env is obvious.
  if (import.meta.env.DEV) {
    console.warn(
      "[supabase] VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY are not set — " +
        "login, signup and the product app will not work until they are.",
    );
  }
}

/**
 * Browser Supabase client. supabase-js guards storage access for SSR
 * (no window → in-memory fallback), so this is safe to import on the server;
 * a real session is only ever read on the client.
 */
export const supabase = createClient(url, anonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});

export const isSupabaseConfigured = Boolean(url && anonKey);
