// Web Push — PUBLIC value only.
//
// This is the VAPID *public* key. It is safe to commit and to ship in browser code — it only lets
// the browser verify that pushes come from whoever holds the matching PRIVATE key. The PRIVATE key
// (and the Supabase service_role key) live ONLY in GitHub Actions secrets — never here.
//
// SETUP (one time): generate a VAPID key pair, then
//   • paste the PUBLIC key below,
//   • add the PRIVATE key as the GitHub secret VAPID_PRIVATE_KEY.
// Generate the pair (no Node needed):
//   pip3 install pywebpush && python3 pipeline/gen_vapid.py
//
// Until this is filled in, the app simply hides the reminders toggle — everything else works.
window.PUSH_PUBLIC_KEY = "";
