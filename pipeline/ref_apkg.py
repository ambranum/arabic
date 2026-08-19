#!/usr/bin/env python3
"""Inventory the Lingualism Anki deck (verification use only — never shipped).

An .apkg is a zip holding an SQLite db (collection.anki2) plus numbered media files
mapped by a JSON manifest. This prints the note model, field names, a few sample rows
and the media census, so verification scripts know what the deck can corroborate
(e.g. native-recorded verb audio exists, but is copyrighted — we only ever COMPARE
against it, we don't ship it).

Run: python3 pipeline/ref_apkg.py
"""
import json, os, sqlite3, sys, tempfile, zipfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
APKG = os.path.join(ROOT, 'reference', 'Palestinian Arabic Verbs - Lingualism.apkg')


def main():
    if not os.path.exists(APKG):
        print('apkg not present — nothing to inventory (expected on CI).'); return 0
    with zipfile.ZipFile(APKG) as z, tempfile.TemporaryDirectory() as td:
        names = z.namelist()
        dbname = 'collection.anki21' if 'collection.anki21' in names else 'collection.anki2'
        z.extract(dbname, td)
        media = json.loads(z.read('media')) if 'media' in names else {}
        db = sqlite3.connect(os.path.join(td, dbname))
        (models_json,) = db.execute('select models from col').fetchone()
        models = json.loads(models_json)
        for mid, m in models.items():
            print('model:', m['name'], '· fields:', [f['name'] for f in m['flds']])
        n = db.execute('select count(*) from notes').fetchone()[0]
        print('notes:', n)
        for (flds,) in db.execute('select flds from notes limit 3'):
            print('  sample:', flds.replace('\x1f', ' | ')[:160])
        exts = {}
        for fname in media.values():
            exts[os.path.splitext(fname)[1]] = exts.get(os.path.splitext(fname)[1], 0) + 1
        print('media:', len(media), 'files', exts)
    return 0


if __name__ == '__main__':
    sys.exit(main())
