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
| b016 | ok | - | - |
| b017 | ok | minors fixed in b056: Regina addresses 老魔法使い殿 as "honored wizard", not "old wizard" (r076_2716, r076_2B51, r076_334A, r076_33AB); r076_2801 stray comma | - |
| b018 | ok | - | - |
| b019 | ok | Ritten old man のぅ reworked (r085_0D58, r085_0DDA, r085_0EDC, b056); minors r085_0498, r085_084A punctuation (b056) | r085_0C94 ("eh" on every sentence) |
| b020 | ok | minors fixed in b056: r085_168C, r086_03AF, r089_003C punctuation | - |
| b021 | ok | minors fixed in b056: r095_06D4 punctuation, r095_0DE6 caption tense | - |
| b022 | ok | - | - |
| b023 | ok | r109_0667 長いモン "long things" (unwanted double meaning) -> "long swords" (b056) | - |
| b024 | ok | Landburg item-shop granny じゃ/のう voice flattened: r110_0053, r110_024D, r110_03AB, r111_0127, r111_0205 ("dearie", "mark me", b056) | - |
| b025 | ok | r116_0062 garbled "in see, that house" (b056) | r118_0067 (caption tense) |
| b026 | ok | r118_0B57 hyphen-split "crafts-men", r118_074D caption tense (b056) | - |
| b027 | ok | minor fixed in b056: r121_006F "Borg, and his friends" | - |
| b028 | ok | r121_073F Svart garbled ("decided to help but!", "one over on me, Svart"), b057 | - |
| b029 | ok | Yaak shaman じゃ voice: r135_0305, r135_0417, r135_04B9 (b057) | - |
| b030 | ok | - | - |
| b031 | ok | - | - |
| b032 | ok | minor fixed in b057: r144_04BB run-on | - |
| b033 | ok | - | - |
| b034 | ok | - | - |
| b035 | ok | - | - |
| b036 | ok | - | - |
| b037 | ok | minor fixed in b057: r187_0612 "tell Yuri-sama in Eldar so" | - |
| b038 | ok | Ude ruins old man (Eld's ghost) じゃ/のぅ voice: r192_023C, r192_0332, r192_03DE, r192_0458, r192_04A7, r192_04DB, r192_1095 (b057) | - |
| b039 | ok | - | - |
| b040 | ok | Kroket old men じゃ/のぅ voice: r195_0048, r195_00C6, r197_00A1; r198_068E caption tense (b057) | - |
| b041 | ok | r198_09A0 book 『真の言葉の使い手』 said "master(s) of the (true) word": now "true word-speaker" (glossary); r204_06C6 stutter typos (b057) | - |
| b042 | ok | minor fixed in b057: chant "Stor...Dod" spacing r239_025B, r239_0353 | - |
| b043 | ok | minor: r244_07AF mage じゃ tag (b057) | - |
| b044 | ok | r255_098C Lidar "is about me alone" (b057) | - |
| b045 | ok | Nordrig old man じゃ voice: r257_0044, r257_018A (b057) | - |
| b046 | ok | r293_00AE Iskar "rightful/real master of the true words" -> "true word-speaker" (matches b054); Eldar Elder じゃ voice r309_0660, r309_06A6 (b057) | - |
