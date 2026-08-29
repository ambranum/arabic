# A4 — eleven_v3 Hebrew

Voices: Adam `s3TPKV1kjDlVtZbl4Ksh`, Jessica `r1KmysJdVYZjJCm4mL3b`  ·  model `eleven_v3`  ·  seed `20260829`

## 0. Model and language probe

OK — `eleven_v3` accepted `language_code: he`, 86979 bytes for the test sentence.

`audio/probe-he.mp3`

## 1. Determinism (same text, same seed, twice)

**DIFFERENT** — seed is best-effort only; a re-voice can change a clip. Clips must be cached and never regenerated casually.

`86979` vs `86979` bytes

## 2. Does it honour niqqud?

Identical audio across different pointings would mean the niqqud is being stripped. Different audio means it is being read — whether *correctly* is what the clips are for.

### sefer

| text | reading | bytes | sha256[:12] | clip |
|---|---|---|---|---|
| ספר | bare | 31808 | c5882baa5f99 | `audio/sefer-0.mp3` |
| סֵפֶר | sefer = book | 23031 | ec8a1d8c297b | `audio/sefer-1.mp3` |
| סַפָּר | sapar = barber | 15090 | b1314f2c03c9 | `audio/sefer-2.mp3` |
| סִפֵּר | siper = he told | 28047 | abb8bd02483b | `audio/sefer-3.mp3` |
| סָפַר | safar = he counted | 30555 | cdafcd6ac056 | `audio/sefer-4.mp3` |

5 distinct renderings out of 5 inputs — **the pointing is being read**

### boker

| text | reading | bytes | sha256[:12] | clip |
|---|---|---|---|---|
| בקר | bare | 11328 | 3a218d803c36 | `audio/boker-0.mp3` |
| בֹּקֶר | boker = morning | 8821 | f4ccd01a6eb6 | `audio/boker-1.mp3` |
| בָּקָר | bakar = cattle | 28047 | 316594fa6605 | `audio/boker-2.mp3` |
| בִּקֵּר | biker = he visited | 28047 | 93d4015bdaf1 | `audio/boker-3.mp3` |

4 distinct renderings out of 4 inputs — **the pointing is being read**

### oxel

| text | reading | bytes | sha256[:12] | clip |
|---|---|---|---|---|
| אכל | bare | 10075 | a94b3d4a9ae2 | `audio/oxel-0.mp3` |
| אֹכֶל | oxel = food | 10075 | 1a5343fe4091 | `audio/oxel-1.mp3` |
| אָכַל | axal = he ate | 12582 | 52a1b24b8029 | `audio/oxel-2.mp3` |
| אוֹכֵל | oxel = eating (male) | 17598 | e9dacd9c64c5 | `audio/oxel-3.mp3` |

4 distinct renderings out of 4 inputs — **the pointing is being read**

## 3. Single words

The vocabulary bank is 1,843 one-word clips. Each word below is synthesized twice: bare, and with an unspoken carrier via `previous_text`/`next_text`. Listen to both columns — if the bare clips are clipped, rushed or oddly intoned, the carrier is the fix.

| word | bare | bytes | carried | bytes |
|---|---|---|---|---|
| שָׁלוֹם | `audio/word-00-bare.mp3` | 10075 | `audio/word-00-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"2ab3f93effd8b2d436f5b0856465edf6","param":"model_id"}} |
| תּוֹדָה | `audio/word-01-bare.mp3` | 10075 | `audio/word-01-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"1e59e2ac7c064bf1b0738bbcfeea8699","param":"model_id"}} |
| בְּבַקָּשָׁה | `audio/word-02-bare.mp3` | 16344 | `audio/word-02-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"c7976f7de6d46301b09ebcafbb1f907b","param":"model_id"}} |
| סְלִיחָה | `audio/word-03-bare.mp3` | 21359 | `audio/word-03-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"2cf38350514a503f737ff55eeec854e5","param":"model_id"}} |
| כֵּן | `audio/word-04-bare.mp3` | 7567 | `audio/word-04-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"2d40a8239bb65f4a737ff55eeec8572b","param":"model_id"}} |
| לֹא | `audio/word-05-bare.mp3` | 12582 | `audio/word-05-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"79c67c44ff74ba3c5d1ba7f7db4dbb5a","param":"model_id"}} |
| מַיִם | `audio/word-06-bare.mp3` | 25539 | `audio/word-06-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"928ed0f2ea0e41e9737ff55eeec85b89","param":"model_id"}} |
| לֶחֶם | `audio/word-07-bare.mp3` | 30555 | `audio/word-07-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"8999f6a41356b466ce237b71d75d8ef7","param":"model_id"}} |
| בַּיִת | `audio/word-08-bare.mp3` | 24285 | `audio/word-08-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"6fcce970884ced2ff2e0eedfd4f8305b","param":"model_id"}} |
| יֶלֶד | `audio/word-09-bare.mp3` | 38078 | `audio/word-09-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"d7992da6b7311a82ed23d06fd266cffd","param":"model_id"}} |
| אִמָּא | `audio/word-10-bare.mp3` | 20106 | `audio/word-10-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"1507469de8bea7aa6df4806412bbe471","param":"model_id"}} |
| אַבָּא | `audio/word-11-bare.mp3` | 20106 | `audio/word-11-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"e4843bc085661df7aeb14da528fc437f","param":"model_id"}} |
| חָבֵר | `audio/word-12-bare.mp3` | 11328 | `audio/word-12-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"140f1a3c86527c8f0314e8ac734a48e1","param":"model_id"}} |
| עֶרֶב | `audio/word-13-bare.mp3` | 18852 | `audio/word-13-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"6c09dbd82e60008a598c58bdf36f1280","param":"model_id"}} |
| בֹּקֶר | `audio/word-14-bare.mp3` | 8821 | `audio/word-14-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"80ffb3988b503e920314e8ac734a4845","param":"model_id"}} |
| לַיְלָה | `audio/word-15-bare.mp3` | 18852 | `audio/word-15-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"c8a9cf81f232483a4f260979fe252d4b","param":"model_id"}} |
| גָּדוֹל | `audio/word-16-bare.mp3` | 25539 | `audio/word-16-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"5a7a6f73a4cb4913bfea6411c3788a5c","param":"model_id"}} |
| קָטָן | `audio/word-17-bare.mp3` | 11328 | `audio/word-17-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"0d0cb91d506716724f260979fe2524d0","param":"model_id"}} |
| יָפֶה | `audio/word-18-bare.mp3` | 28047 | `audio/word-18-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"94a3a02546eea293a52e9eb852dcc1a1","param":"model_id"}} |
| טוֹב | `audio/word-19-bare.mp3` | 8821 | `audio/word-19-carried.mp3` | HTTP 400 {"detail":{"type":"validation_error","code":"unsupported_model","message":"Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.","status":"unsupported_model","request_id":"5377f378c99879a6bfea6411c37889fc","param":"model_id"}} |

## 4. Second voice (Jessica)

Needed so `cast_dialogue()` can gender-match speakers in the lesson dialogues and the Shabbat-table conversations.

OK, 76530 bytes — `audio/jessica-sentence.mp3`

---

# Analysis (added after the run)

The script's own pass/fail lines are not all trustworthy, and one of them is wrong in a way
worth writing down.

## The niqqud test needed a control, and got one

Section 2 concluded "the pointing is being read" from the audio hashes being different. That
inference does not hold on its own, because **section 1 proved the same text produces different
audio.** Different bytes cannot distinguish "read the pointing" from "drifted between runs".

Decoding the clips gives a control that does work — **duration**:

| | |
|---|---|
| same text, twice (det-1, det-2) | 5.36s and 5.36s — *identical* |
| ספר / סֵפֶר / סַפָּר / סִפֵּר / סָפַר | 1.92 / 1.36 / 0.88 / 1.68 / 1.84s |
| בקר / בֹּקֶר / בָּקָר / בִּקֵּר | 0.64 / 0.48 / 1.68 / 1.68s |

Duration is stable under repetition and moves with the pointing. **The niqqud is being read.**
Whether each one is read *correctly* still needs an ear — the clips are in `spike/he/audio/`.

Note אכל and אֹכֶל come out the same length, which is the expected answer rather than a failure:
bare אכל should default to the commonest reading, and that is *oxel*.

## Determinism fails, and it is not a metadata artefact

det-1 and det-2 are byte-identical in *size* and identical in duration, so the obvious guess is
an ID3 timestamp. It is not: decoding both to raw PCM gives different hashes. Same text, same
seed, genuinely different audio.

**Operational consequence, and it is sharp:** `pipeline/regen_audio.sh` deletes clips before
re-voicing. Under v3 that would silently change the reading of every word in the corpus. Hebrew
clips have to be generated once and treated as immutable; a re-voice is a content change, not a
refresh.

## Single words are NOT stable, and the planned mitigation is unavailable

`previous_text` / `next_text` return a clean 400 on v3:

> `Providing previous_text or next_text is not yet supported with the 'eleven_v3' model.`

That was the carrier trick, and it is off the table on the only model that speaks Hebrew.

It is needed. Across the sixteen two-syllable words, seconds-per-syllable runs from **0.24 to
1.16 — a 4.8× spread**:

| | | | |
|---|---|---|---|
| בֹּקֶר *boker* | 0.48s | שָׁלוֹם *shalom* | 0.56s |
| חָבֵר *xaver* | 0.64s | אִמָּא *ima* | 1.20s |
| לֶחֶם *lexem* | 1.84s | יֶלֶד *yeled* | **2.32s** |

"Yeled" is two syllables and takes 2.32 seconds. The expressive model is doing expressive things
to a word with no context to be expressive about.

**The fix to try next** is the timestamps endpoint,
`/v1/text-to-speech/{voice_id}/with-timestamps`, which returns character-level alignment. Put
the word in a real carrier sentence, synthesize once, and slice the word out on the returned
offsets. That gets the carrier's prosody without the unsupported parameter, and it is how the
1,843-word bank should probably be built regardless.
