#!/usr/bin/env python3
"""Generate a VAPID key pair for Web Push — no Node required.

Prints two keys:
  • PUBLIC  → paste into app/data/pushconfig.js  (window.PUSH_PUBLIC_KEY)  — safe to commit
  • PRIVATE → paste into the GitHub secret  VAPID_PRIVATE_KEY               — keep secret

Both are single-line base64url. The private key is your machine's to keep; it is printed here only
so you can copy it into the GitHub secret. It is never sent anywhere by this script.

    pip3 install pywebpush          # brings in the 'cryptography' library this needs
    python3 pipeline/gen_vapid.py
"""
import base64, sys

try:
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
except ModuleNotFoundError:
    sys.exit("Missing dependency. Run:  pip3 install pywebpush   (then re-run this script)")


def b64u(b):
    return base64.urlsafe_b64encode(b).decode().rstrip('=')


key = ec.generate_private_key(ec.SECP256R1())

# Browser applicationServerKey: the 65-byte uncompressed public point (0x04 ‖ X ‖ Y), base64url.
pub = key.public_key().public_bytes(
    serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
# VAPID private key: the raw 32-byte private scalar, base64url — the form py_vapid/pywebpush accept.
priv = key.private_numbers().private_value.to_bytes(32, "big")

print("=" * 68)
print("PUBLIC KEY  → app/data/pushconfig.js   window.PUSH_PUBLIC_KEY = \"...\"")
print("  " + b64u(pub))
print()
print("PRIVATE KEY → GitHub secret  VAPID_PRIVATE_KEY   (keep this secret)")
print("  " + b64u(priv))
print("=" * 68)
