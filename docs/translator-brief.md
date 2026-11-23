# Translator brief (phase 6)

Orca runs have no subagents and `codex exec` may be out of quota: the session translates batches itself. Keep each
Read under ~4 KB (the context-mode hook stubs larger ones): read a batch with `limit` 60-75 lines at a time.

## Read first
- `glossary.md` (rulings, style, names; binding), `docs/decisions.md` D9-D11.
- Box budgets: `docs/re/windows.md`. The batch tool knows them; the `limit` column of each batch row says which.

## Loop per batch
1. `work/tl/bNNN.tsv`: `id<TAB>speaker<TAB>form<TAB>limit<TAB>jp` (batches already split: b001-b049; `batches.py split`
   numbers on and never re-batches an id that is in an existing batch file).
2. Write `work/tl/bNNN.out.tsv` (`id<TAB>English`, every id once, same order) with the file-write tool; for a long batch
   write `bNNN.p1`, `bNNN.p2` and `cat` them into the `.out.tsv`.
3. `python -X utf8 tools/batches.py check bNNN` until OK; `show bNNN` prints the wrapped result with pixel widths;
   `fit "text"` tries one line.
4. `sh tools/merge_batch.sh bNNN`: merge, build (the hard gate: a slot under 5 bytes can't relocate), `check.py`,
   commit `script/` + `glossary.md` with the batch number. After fixing an already merged batch: `batches.py merge
   bNNN --overwrite`.

## Format rules (what the tool does and doesn't do)
- `dlg`: write running text per page; the tool wraps each `{page}` segment that has no `{nl}` to 208 px and indents
  continuation lines of a `"` speech by one space. Max 3 lines per page: add `{page}` where needed. If you write `{nl}`
  in a page, your breaks are kept as they are (used for item descriptions and fixed layouts).
- Speech: `"` opens, no closing quote (JP 「 has no 」). Narration has no quote.
- Speaker pages: write `Name{nl}"speech...` (one `{nl}` after the name, none in the speech): the tool keeps the name
  line and wraps the speech; the name is one of the 3 lines. Leading control tokens (`{FB00}`, `{F9FF}{D340}`) stay
  in front of the name. When the English has as many pages as the JP, a JP page starting with a letter (no 「, no
  leading space, no name line) is narration and is not indented. Choice lines `{F600}...` are never indented.
- Inner quotes: use single quotes ('rite'), never `"` mid-speech. Avoid the word "May" (glossary Avoid for メイ).
- Battle rects: dropped from b002 and left for phase 7 engine work: run-time particles `bt_198045` の, `bt_1980E3`
  に, `bt_19D534/38/3C` し/ま/た and `bt_19D4BB` (クルト + kanji pieces, meaning unknown until seen in game).
  bg3_A729/A737/A73D (equip slots ぶき/たて/あし, 4-byte slots, 2 tiles) stay Japanese for phase 7 to repoint.
- Keep every `{token}` except `{nl}` `{page}` `{wait}` (free) and, in menus, `{009F}` (the 。 tile: write `.`).
  Battle rects (`bt_*`) may drop the dakuten tokens (`{2094}`...): rows split by `{nl}`, each row <= w chars, <= h rows.
- `menu`: fixed 8 px tiles, charset `A-Z a-z 0-9 ',.-!?&/:+` and space, no `;` or `"`. One line per JP line;
  leading spaces are recomputed (centred on the JP line). `MENU_CAP` in `tools/batches.py` holds list windows wider
  than their string.
- `name`: items/tactics <= 12 (D10), spells <= 8 (and name + " A" must split into two 8-tile rows), enemies <= 16 as
  two words of <= 8.

## Notes from earlier batches
- enemy_40 / enemy_69 (kanji-byte names `[2A][29]`, `[28][29][2B]`) were dropped from b003: shoot them in battle
  first (phase 8). bg3_9EF0 / bg3_9EF8 (shop Buy/Sell, 2-tile slots) and bg3_A687 (feather note) stay Japanese
  until phase 7 repoints them; skip them if a new split picks them up.
- Status labels are abbreviated by tile count (Atk/Def/Agi/Wis/Lck, Psn/Par, Sys., Ster, Regi): flagged in D11.
- Item names used in descriptions must match `script/items.json` exactly (Herb, Cure Herb, Revive Herb, Seal Stone...).
- 力 = Strength (stat messages) but the 6-tile boxes say "power"; 守備/しゅび = Defense ("guard" in 6-tile boxes).
