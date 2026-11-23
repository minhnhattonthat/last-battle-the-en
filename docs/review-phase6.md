# Phase 6 review (2026-11-24, session 15)

Reviewer: the translating session in a separate read-only pass (no reviewer subagents in this run; `codex exec` out of
quota until 2026-11-26, checked). Not an independent reviewer: a fresh `codex exec -s read-only` story pass is still
worth running before release (phase 8).

## Method
1. `tools/batches.py check` on b001-b049: 0 problems except b005's three 2-tile slots (shop Buy/Sell, `bg3_A687`),
   which are left Japanese by D11 for phase 7 to repoint. Merged script: 3085 entries, 0 problems.
2. Mechanical sweep of all shipped English (Japanese left, a/an before tokens, em dashes, curly quotes, closing
   quotes, double spaces, old name spellings, common typos): 0 hits beyond D1 honorifics and one column-aligned
   mercenary card (`r198_08DA`).
3. Read pairs: random samples of ~60 story entries across r000-r266, 14 BG3 menu/description strings, and all of
   b046-b049 (ending, spells, tactics, shops) while writing them.

## Verdict
- Critical: none. Important: none.
- Minor: 5, in `docs/polish.md`.

## Not done here
- 11 entries left (`work/tl/b050.tsv`): battle particles built at run time, enemy_40/69, 2-tile equipment labels:
  engine work (phase 7), per `docs/re/battle.md`.
- Visual check of speaker pages: phase 8 tours.
