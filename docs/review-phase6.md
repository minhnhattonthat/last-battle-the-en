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
