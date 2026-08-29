#!/usr/bin/env python3
"""A4: does eleven_v3 actually speak Hebrew the way this app needs?

Run it yourself -- the key stays in your environment and is never printed, logged, or written
to the report:

    ELEVENLABS_API_KEY=... python3 spike/he/voice_test.py

Writes spike/he/FINDINGS-voice.md and the clips to spike/he/audio/. Costs a few hundred
characters, which is pennies.

"Can it say Hebrew" is the easy question and the answer is already yes -- Hebrew is in
eleven_v3's language list where it is absent from eleven_multilingual_v2's. The two questions
that decide whether it is USABLE here are harder, and both are measured rather than guessed:

  1. DOES IT HONOUR NIQQUD?  The app shows vocalized Hebrew and has to sound like what it
     shows. Unpointed ספר is genuinely four words -- sefer (book), sapar (barber), siper (he
     told), safar (he counted). If the model strips the pointing, every one of them comes out
     the same and the app teaches the wrong word with a straight face.

     Tested WITHOUT needing ears: synthesize each vocalization with a fixed seed and hash the
     audio. Identical bytes across different pointings means the niqqud was thrown away. Any
     difference means it was read. Whether it was read CORRECTLY still needs a human, which is
     what the clips are for.

  2. IS IT STABLE ON ONE WORD?  The vocabulary bank is 1,843 single-word clips and v3 is the
     expressive, context-driven model. Each word is synthesized bare and again with an unspoken
     carrier (previous_text/next_text), so the two can be compared by ear.

Also checks that language_code is accepted on v3 (it is rejected on multilingual_v2) and that
`seed` really does make generation repeatable -- v3's own docs warn that identical inputs may
drift, which for a corpus that gets rebuilt would silently change readings.
"""
import hashlib
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, 'audio')
REPORT = os.path.join(HERE, 'FINDINGS-voice.md')

VOICES = {'Adam': 's3TPKV1kjDlVtZbl4Ksh', 'Jessica': 'r1KmysJdVYZjJCm4mL3b'}
MODEL = 'eleven_v3'
SEED = 20260829

try:
    import certifi
    CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    CTX = ssl.create_default_context()

# Same consonants, different pointing, genuinely different words.
HOMOGRAPHS = [
    ('sefer', [('ספר', 'bare'), ('סֵפֶר', 'sefer = book'), ('סַפָּר', 'sapar = barber'),
               ('סִפֵּר', 'siper = he told'), ('סָפַר', 'safar = he counted')]),
    ('boker', [('בקר', 'bare'), ('בֹּקֶר', 'boker = morning'), ('בָּקָר', 'bakar = cattle'),
               ('בִּקֵּר', 'biker = he visited')]),
    ('oxel', [('אכל', 'bare'), ('אֹכֶל', 'oxel = food'), ('אָכַל', 'axal = he ate'),
              ('אוֹכֵל', 'oxel = eating (male)')]),
]

# Everyday words a beginner meets in week one.
WORDS = ['שָׁלוֹם', 'תּוֹדָה', 'בְּבַקָּשָׁה', 'סְלִיחָה', 'כֵּן', 'לֹא', 'מַיִם', 'לֶחֶם',
         'בַּיִת', 'יֶלֶד', 'אִמָּא', 'אַבָּא', 'חָבֵר', 'עֶרֶב', 'בֹּקֶר', 'לַיְלָה',
         'גָּדוֹל', 'קָטָן', 'יָפֶה', 'טוֹב']
CARRIER_PREV = 'הוא אמר את המילה'
CARRIER_NEXT = 'ואז הוא שתק.'

SENTENCE = 'הַיֶּלֶד הַקָּטָן אָכַל אֶת הַלֶּחֶם בַּבֹּקֶר, וְאָמַר תּוֹדָה לְאִמָּא שֶׁלּוֹ.'


def tts(key, text, voice_id, tag, prev=None, nxt=None, seed=SEED, lang='he', model=MODEL):
    body = {'text': text, 'model_id': model, 'seed': seed}
    if lang:
        body['language_code'] = lang
    if prev:
        body['previous_text'] = prev
    if nxt:
        body['next_text'] = nxt
    req = urllib.request.Request(
        'https://api.elevenlabs.io/v1/text-to-speech/' + voice_id,
        data=json.dumps(body).encode('utf-8'),
        headers={'content-type': 'application/json', 'xi-api-key': key})
    try:
        with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
            audio = r.read()
    except urllib.error.HTTPError as e:
        detail = ''
        try:
            detail = e.read().decode('utf-8', 'replace')[:300]
        except Exception:
            pass
        return None, 'HTTP %s %s' % (e.code, detail)
    except Exception as e:
        return None, str(e)[:160]
    path = os.path.join(OUTDIR, tag + '.mp3')
    with open(path, 'wb') as f:
        f.write(audio)
    return audio, None


def main():
    key = os.environ.get('ELEVENLABS_API_KEY')
    if not key:
        print('ELEVENLABS_API_KEY is not set. Run:\n'
              '  ELEVENLABS_API_KEY=... python3 spike/he/voice_test.py', file=sys.stderr)
        return 2
    os.makedirs(OUTDIR, exist_ok=True)
    voice = VOICES['Adam']
    out = ['# A4 — eleven_v3 Hebrew', '',
           'Voices: Adam `%s`, Jessica `%s`  ·  model `%s`  ·  seed `%d`'
           % (VOICES['Adam'], VOICES['Jessica'], MODEL, SEED), '']

    # ---- 0. does the model/language combination work at all? ---------------------------
    print('probing model + language_code ...')
    audio, err = tts(key, SENTENCE, voice, 'probe-he')
    out += ['## 0. Model and language probe', '']
    if err:
        out += ['**FAILED** with `language_code: he` on `%s`: `%s`' % (MODEL, err), '']
        a2, e2 = tts(key, SENTENCE, voice, 'probe-nolang', lang=None)
        out += ['Without `language_code`: %s' % ('**FAILED** `%s`' % e2 if e2
                                                 else 'OK, %d bytes' % len(a2)), '']
        if e2:
            a3, e3 = tts(key, SENTENCE, voice, 'probe-v2', lang=None,
                         model='eleven_multilingual_v2')
            out += ['On `eleven_multilingual_v2`: %s' % ('FAILED `%s`' % e3 if e3
                                                         else 'OK, %d bytes' % len(a3)), '']
            open(REPORT, 'w').write('\n'.join(out))
            print('probe failed; see', REPORT)
            return 1
    else:
        out += ['OK — `%s` accepted `language_code: he`, %d bytes for the test sentence.'
                % (MODEL, len(audio)), '', '`audio/probe-he.mp3`', '']

    # ---- 1. determinism ----------------------------------------------------------------
    print('determinism ...')
    a1, _ = tts(key, SENTENCE, voice, 'det-1')
    time.sleep(1)
    a2, _ = tts(key, SENTENCE, voice, 'det-2')
    same = bool(a1 and a2 and hashlib.sha256(a1).digest() == hashlib.sha256(a2).digest())
    out += ['## 1. Determinism (same text, same seed, twice)', '',
            '**%s** — %s' % ('identical' if same else 'DIFFERENT',
                             'a rebuild will not silently change readings.' if same else
                             'seed is best-effort only; a re-voice can change a clip. '
                             'Clips must be cached and never regenerated casually.'),
            '', '`%d` vs `%d` bytes' % (len(a1 or b''), len(a2 or b'')), '']

    # ---- 2. niqqud fidelity ------------------------------------------------------------
    print('niqqud fidelity ...')
    out += ['## 2. Does it honour niqqud?', '',
            'Identical audio across different pointings would mean the niqqud is being '
            'stripped. Different audio means it is being read — whether *correctly* is what '
            'the clips are for.', '']
    for name, variants in HOMOGRAPHS:
        rows, hashes = [], {}
        for i, (text, label) in enumerate(variants):
            tag = '%s-%d' % (name, i)
            a, e = tts(key, text, voice, tag)
            h = hashlib.sha256(a).hexdigest()[:12] if a else 'ERROR'
            hashes[h] = hashes.get(h, 0) + 1
            rows.append('| %s | %s | %s | %s | `audio/%s.mp3` |'
                        % (text, label, len(a) if a else e, h, tag))
            time.sleep(0.4)
        distinct = len([h for h in hashes if h != 'ERROR'])
        out += ['### %s' % name, '',
                '| text | reading | bytes | sha256[:12] | clip |',
                '|---|---|---|---|---|'] + rows + ['',
                '%d distinct renderings out of %d inputs — **%s**'
                % (distinct, len(variants),
                   'the pointing is being read' if distinct > 1
                   else 'IDENTICAL: the pointing is being ignored'), '']

    # ---- 3. single words, bare vs carried ----------------------------------------------
    print('single words ...')
    out += ['## 3. Single words', '',
            'The vocabulary bank is 1,843 one-word clips. Each word below is synthesized twice: '
            'bare, and with an unspoken carrier via `previous_text`/`next_text`. Listen to both '
            'columns — if the bare clips are clipped, rushed or oddly intoned, the carrier is '
            'the fix.', '',
            '| word | bare | bytes | carried | bytes |', '|---|---|---|---|---|']
    for i, w in enumerate(WORDS):
        b, be = tts(key, w, voice, 'word-%02d-bare' % i)
        time.sleep(0.3)
        c, ce = tts(key, w, voice, 'word-%02d-carried' % i,
                    prev=CARRIER_PREV, nxt=CARRIER_NEXT)
        time.sleep(0.3)
        out.append('| %s | `audio/word-%02d-bare.mp3` | %s | `audio/word-%02d-carried.mp3` | %s |'
                   % (w, i, len(b) if b else be, i, len(c) if c else ce))
    out += ['']

    # ---- 4. the other voice ------------------------------------------------------------
    print('second voice ...')
    a, e = tts(key, SENTENCE, VOICES['Jessica'], 'jessica-sentence')
    out += ['## 4. Second voice (Jessica)', '',
            'Needed so `cast_dialogue()` can gender-match speakers in the lesson dialogues and '
            'the Shabbat-table conversations.', '',
            '%s — `audio/jessica-sentence.mp3`'
            % ('OK, %d bytes' % len(a) if a else '**FAILED** `%s`' % e), '']

    open(REPORT, 'w').write('\n'.join(out))
    print('\n-> %s' % REPORT)
    print('-> %d clips in %s' % (len(os.listdir(OUTDIR)), OUTDIR))
    return 0


if __name__ == '__main__':
    sys.exit(main())
