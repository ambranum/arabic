#!/usr/bin/env python3
"""One HTTPS context for the whole pipeline, and one explanation when it fails.

Nine files had grown the same five lines: try certifi, fall back to the default context. The
fallback is the problem. On a macOS python.org build the default context has no CA bundle wired
up, so it does not fail at import -- it fails at the first request, with

    <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed

which says nothing about the actual cause and is indistinguishable from a network problem. And
because each caller caught it per item, a run could print that line once per word, fifty-eight
times, and still exit 0 having written a data file that says "audio 0/58".

The actual cause, every time so far, has been the INTERPRETER: `python3` on the PATH is not the
one the project's dependencies are installed for. certifi is in requirements.txt, so its absence
is the tell, and this says so by name instead of leaving a TLS error to be interpreted.
"""
import ssl
import sys
import urllib.error

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
    HAVE_CERTIFI = True
except Exception:
    SSL_CTX = ssl.create_default_context()
    HAVE_CERTIFI = False


def need(module):
    """Import a third-party dependency, or say which interpreter is missing it.

    Same failure as the certifi one and the same cause: `python3` on the PATH is not the one
    this project's dependencies are installed for. A bare ModuleNotFoundError does not say that.
    """
    try:
        return __import__(module)
    except ImportError:
        raise SystemExit(
            "\n!! %s is not installed for %s\n"
            "   It is in requirements.txt, so this is probably the wrong interpreter.\n"
            "   Install it here:  %s -m pip install -r requirements.txt"
            % (module, sys.executable, sys.executable))


SPENT = ('quota_exceeded', 'credits remaining', 'insufficient', 'out of credit',
         'billing', 'payment')


def explain(e, body=''):
    """-> (what went wrong, what to do about it). ('', '') if this is not a transport failure.

    `body` is the response text, when the caller has already read it -- an HTTPError can only be
    read once, and every caller here reads it to print.
    """
    msg = str(e)
    if isinstance(e, urllib.error.HTTPError):
        if not body:
            try:
                body = e.read().decode('utf-8', 'replace')
            except Exception:
                body = ''
        # A 401 does not always mean what it says. ElevenLabs answers a spent balance with 401
        # and "quota_exceeded" in the body, so the honest reading of the status alone -- "the
        # API rejected the key" -- sent a perfectly good key off to be regenerated while the
        # actual problem was a bill. The body settles it, and is checked before the code.
        if any(t in body.lower() for t in SPENT):
            return ('the account is out of credit (HTTP %d, %s)'
                    % (e.code, body.strip()[:90].replace('\n', ' ')),
                    'Top up the balance for whichever service this was. The key is fine.')
        # Most HTTP answers are about the request. These are about the RUN: the next item will
        # get exactly the same one, so fifty-eight of them is fifty-seven too many.
        if e.code in (401, 403):
            return ('the API rejected the key (HTTP %d)' % e.code,
                    'Check ELEVENLABS_API_KEY / ANTHROPIC_API_KEY in this shell — expired, '
                    'revoked, or from the wrong account.')
        if e.code in (402, 429):
            return ('the account is out of credit or rate limited (HTTP %d)' % e.code,
                    'Check the balance; a rate limit usually clears on its own.')
        return '', ''                      # anything else is the caller's to read
    if 'CERTIFICATE_VERIFY' in msg and not HAVE_CERTIFI:
        return ('HTTPS certificates cannot be verified, and certifi is not installed for %s'
                % sys.executable,
                'That interpreter is not the one this project\'s dependencies are installed for.'
                '\n   Run the command again with the interpreter that has them, or install them'
                '\n   here:  %s -m pip install -r requirements.txt' % sys.executable)
    if 'CERTIFICATE_VERIFY' in msg:
        return ('HTTPS certificates cannot be verified even with certifi\'s bundle',
                'Usually a proxy or VPN intercepting TLS. Try again off it.')
    if isinstance(e, urllib.error.URLError) or 'urlopen error' in msg:
        return ('could not reach the server: %s' % msg[:120],
                'Check the network; nothing is wrong with the data.')
    return '', ''


def fatal(e, prefix='', body=''):
    """Print the diagnosis and stop. Transport failures do not get better on the next item."""
    what, fix = explain(e, body)
    if not what:
        return False
    sys.stdout.flush()          # so the diagnosis lands after the line that provoked it
    print('\n!! %s%s' % (prefix, what), file=sys.stderr)
    if fix:
        print('   %s' % fix, file=sys.stderr)
    return True
