# Reference teaching materials

The user's own Palestinian-Arabic lessons, course notes and drill books. These are the
app's **pedagogical backbone and correctness oracle**:

- their teaching sequence drives `texts/ref/SYLLABUS.md` and the curriculum,
- their content is transcribed into `texts/ref/<book>.json` (each item stamped
  `src: "<book> p.N"`) and adapted into in-app lesson units,
- `pipeline/verify_content.py` audits the app's curated Arabic against them.

Most files are image scans with no text layer — `pipeline/ref_extract.py` renders them
to `build/ref/<slug>/pNNN.png` (local only) so they can be transcribed by reading.

**Two files are NOT committed** (`.gitignore`): the Lingualism *Palestinian Arabic Verbs*
PDF and its Anki deck. They are commercial third-party products, used strictly for
verification (`pipeline/verify_conjugation.py`, `pipeline/book_sweep.py`) — never
transcribed, never shipped, never pushed. This repo is public; do not commit them.

| slug | file | pages | what it is |
|---|---|---|---|
| najah | Najah lessons.pdf | 164 | Full lesson course (the largest source) |
| speaking | Speaking Arabic.pdf | 62 | Spoken-Arabic lessons (identical to "Spoken Arabic Lessons.pdf") |
| spoken-extra | Spoken Arabic Lessons additional.pdf | 24 | Additional spoken lessons |
| vocab-gram | Vocab and Grammar.pdf | 24 | Vocabulary + grammar reference |
| stories | Short Stories.pdf | 26 | Short stories |
| verb-forms | Verb Forms.pdf | 50 | Verb form tables |
| verb-drills | Verb Drills.pdf | 46 | Verb drill exercises (mined mainly for drill FORMATS) |
| — | Palestinian_Arabic_Verbs_-_Lingualism.pdf / .apkg | 171 | **gitignored** — verification only |
