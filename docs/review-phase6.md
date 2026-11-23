# Phase 6 review

## Session 15 (2026-11-24): self-review, superseded
The translating session sampled ~60 story entries and found no Critical/Important. The external phase-6 review
(`.harness/reviews/last-battle-the-en-phase6.md`, outside the repo) rejected it: not independent, ~3% of story lines,
and its own 150-line sample found a flattened voice (Yaak Chief, ぞい) and a title+honorific ("Cardinal-sama"). Phase 6
was reopened in session 16.

## Session 16+ : full per-batch reviewer pass
Method (translation.md §Review): `python -X utf8 tools/pairs.py` writes `work/review/bNNN.txt` (`>> id | JP` / EN,
script order, two `ctx` entries each side). No reviewer subagents in an Orca run and `codex exec` is out of quota until
2026-11-26 10:32 (checked session 16), so the reviewer is a fresh read-only pass by the session, reading every pair
against `glossary.md` and `docs/style-reference.md`, judging accuracy, consistency, naturalness and voice, rating
Critical / Important / Minor. Critical/Important are fixed per batch through fix batches (`tools/fixbatch.py bNNN ids`,
edit `.out.tsv`, `batches.py check` + `merge --overwrite`); Minors go to `docs/polish.md`.

Fixes already made from the external review (fix batches b051, b052): all 16 Yaak Chief lines re-voiced (device in
the style reference), "Cardinal-sama" -> "Your Eminence" / "His Eminence" (`r248_00E5`, `r130_0ABD`), Beebo's
"Feben-sama" / "Kee kee!" (`r076_134A`), `r118_06C1` tense, "Febennels' House" (`b04_B3FC`).

### Batch verdicts
`ok` = no Critical/Important left (after fixes, listed). `todo` = not yet reviewed.

| Batch | Verdict | Fixed (Critical/Important) | Minors to polish.md |
|---|---|---|---|
| b001 | ok | - | bt_140017, bt_186247 |
| b002 | ok | common_0472 old man's のう voice (b053) | bt_1991EC, bt_19E144, bt_1D8301, common_0384 |
| b003 | ok | - | cr_E2BD |
| b004 | ok | - | item_D3 |
| b005 | ok | - (bg3_9EF0/9EF8/A687 untranslated by D11, in polish.md) | - |
| b006 | ok | - | - |
| b007 | ok | Eldar Elder じゃ voice: r002_0038, r002_01FE, r003_053F, r003_06B1 (b053) | - |
| b008 | ok | 真の言葉の使い手 = "true word-speaker" (glossary) in r009_00D8, r009_0144, and Iskar-scene r293_04A5, r293_06A7 that said "master of the true words" (b054) | - |
| b009 | ok | r021_06A4 old castle official のう voice (b055); minors fixed in b055: r020_0DB0 "The mission of us", r020_0898 "the cell" | - |
| b010 | ok | minor fixed in b055: r022_10E2 Mei "Would you not get in the way?" | - |
| b011 | ok | r024_0261 old soldier じゃ voice (b055); minors fixed in b055: King Gustav contractions r025_0239, r025_02F6 | - |
| b012 | ok | - | - |
| b013 | ok | minor fixed in b055: r041_01E2 "the cell" | - |
| b014 | ok | minor fixed in b055: r064_0693 だ・か・ら emphasis | - |
| b015 | ok | minor fixed in b055: r064_097F repeated "So" | - |
