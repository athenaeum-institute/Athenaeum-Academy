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
    storage: window.localStorage,
    storageKey: 'athenaeum-auth',
    experimental: {
      passkey: true
    }
  }
});

// Global XSS Sanitization Utility
window.sanitizeInput = function(str) {
  if (typeof str !== 'string') return '';
  return str
    .trim()
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
};
function sanitizeInput(str) {
  return window.sanitizeInput(str);
}
