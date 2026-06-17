// ============================================================
//  Athenaeum — Supabase Client (v2)
//  Project: hgbaqaofrkljmrvcaisp
// ============================================================

const supabaseUrl     = 'https://hgbaqaofrkljmrvcaisp.supabase.co';
const supabaseAnonKey = 'sb_publishable_FTsvy-qhy1vfn0idE04bPQ_dTLlQZm0';

// Create client (works with both legacy anon-key and new publishable-key formats)
window.supabaseClient = window.supabase.createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken:  true,
    persistSession:    true,
    detectSessionInUrl: true,
    storageKey: 'athenaeum-auth',
    experimental: {
      passkey: true
    }
  }
});
