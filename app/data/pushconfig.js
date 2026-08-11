// Web Push — PUBLIC value only.
//
// This is the VAPID *public* key. It is safe to commit and to ship in browser code — it only lets
// the browser verify that pushes come from whoever holds the matching PRIVATE key. The PRIVATE key
// (and the Supabase service_role key) live ONLY in GitHub Actions secrets — never here.
//
// SETUP (one time): generate a VAPID key pair, then
//   • paste the PUBLIC key below,
//   • add the PRIVATE key as the GitHub secret VAPID_PRIVATE_KEY.
// Generate with either:
//   npx web-push generate-vapid-keys
//   python3 -c "from py_vapid import Vapid01 as V; v=V(); v.generate_keys(); import base64;
//     pub=base64.urlsafe_b64encode(v.public_key.public_bytes(__import__('cryptography').hazmat.primitives.serialization.Encoding.X962, __import__('cryptography').hazmat.primitives.serialization.PublicFormat.UncompressedPoint)).decode().rstrip('='); print('PUBLIC', pub)"
//
// Until this is filled in, the app simply hides the reminders toggle — everything else works.
window.PUSH_PUBLIC_KEY = "";
