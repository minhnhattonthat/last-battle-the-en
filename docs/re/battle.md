# Battle text and graphics (phase 5, 2026-11-23)

Battle code lives in banks $29/$30 (DB = $28 while drawing). Probes: `tools/lua/battle_lz.lua` (battle LZ runs),
`tools/lua/stack_log.lua`, the skill's `watch.lua` / `snes_romreads.lua`; scenes `battle_field`, `battle_room`,
`battle_win`, `wipeout`.

## Names (verified: `battle_field` on the marker build, `work/qa/mbat3`)
- **29:B2B6** draws a byte name as A (always 8) BG3 tile pairs: top row to `[$34]` (the dakuten row), bottom row to
  `[$38]`. Byte 0 = blank; b < $30: 4-byte entry (top word, bottom word) at `$28:8C38 + 4 * (b - $28)` (file
  `0x140C38`; $28-$2E are two-row kanji pieces); else 2 tile bytes (top, bottom) at `$28:8C58 + 2 * (b - $30)` (file
  `0x140C58`), palette `$2000`. FF = blank (names are FF-padded, sometimes FF-centred).
- Callers: 30:AD08 (enemy name window: record from 30:A915), 30:ACB0 (spell cast: default name `$33:D3F1 +
  (type & $1F) * 8`, or the record's custom name at record + 4 when 30:85C8 says so; then the window script
  `$33:D4A1` via 29:A1EA), 29:B309 (tactics name `$1C91 + $1C90 * 12`). Buffers `$14CE` / `$14DE` (8 words each),
  `$14F0` / `$1500`.
- Enemy records: `$2A:A632 + 40 * i` (file `0x152632`), 93 records, name = bytes 2-9 (`script/enemies.json`). The next
  table (10-byte records) is at `$2A:EF5C`. Names `enemy_40` and `enemy_69` use the two-row kanji bytes $28-$2E
  (`[2A][29] `, `[28][29][2B]`): see them in game before translating.
- Tactics: 8 records of 12 bytes copied at new game from file `0x1FEF0` to `$1C91` (03:F8E9), name = first 8 bytes
  (`script/tactics.json`); also shown in the field tactics menu through 01:FEAA (FE7A).
- English (`asm/vwf.asm` bt_name, hook 29:B2B6): a field starting with an escape (`kind, n [, RANK]`, as for items
  and spells; kinds 3 enemies, 4 tactics) draws the name's battle form from `BT_PTRS` ($FC:9100): two 8-char rows
  (`insert.battle_rows`: a name of <= 8 chars centred on the bottom row, a longer one split at a space into two
  centred rows; up to 16 chars). `insert.battle_spells` turns the 22 default spell slots into spell escapes;
  `insert.battle_bytes` maps ASCII party-name bytes (lowercase, NE_PUNCT) in both byte tables.
  Not yet seen in game: the spell-cast window (no scene casts a spell yet) and the rank form.

## Battle font (verified)
BG3 chr at VRAM byte `$C000` in battle is not LZ block 319: it is a copy in the **battle LZ** format at `$2A:8000`
(file `0x150000`, 0xB34 bytes), loaded by 30:F410 from a load list (entry: +2 VRAM word, +4 24-bit source, +7
compressed length; the font's entries are at file `0x14049D` and `0x147365`), decompressed to `$7E2000` (first word =
size $11A0) and DMA'd to VRAM `$6000`. Same tiles as block 319 except tile $48 and $A8-$AE. `font_bg3.battle_patch`
decodes it, draws the English tiles, re-encodes it in place (`tools/blz.py`, 2842 bytes) and writes the new length into
both list entries. Second stream right after it (`0x150B34`, to VRAM `$6C00`): battle status icons and the **party
name graphics** (クルト = tiles $1A4-$1A6 in the status box): graphics text, phase 8.

### Battle LZ (tools/blz.py, decoder 30:F5C1)
2 KB ring window at `$7EC000`, zero-filled, write position 0. `0xxxxxxx yyyyzzzz` = copy z+2 bytes from
pos - (x << 4 | y); `10nnnnnn` = n+1 literals; `11e mm nnn [lo]` = fill, count n+2 (or (n << 8 | lo) + 2 with e),
pattern of mm+1 bytes. The decoder runs while the source < start + length - 1. A copy reads its whole source
before writing (offset < length does not repeat its own output, it reads the window's old bytes): until
2026-11-24 the encoder emitted such copies and every battle showed garbage tiles (lines in the box borders, `!`
as a cross); found by comparing a VRAM dump with `blz.decode`. The encoder now keeps length <= offset.

## Battle messages and screens (extracted: `script/battle.json`, kind `battle`, `tools/battle_text.py`)
BG3 tile words with attribute bits (`$20xx`/`$21xx`/`$60A0`; tiles >= $100 are kanji or two-row pieces, `$94` is the
dakuten on the row above the kana). Window-script interpreter **29:A1EA** (A = script address in bank $33):
`00 dest(2,$7E) src(3) w h` copies a w x h rectangle of tile words (rows contiguous at src) into the WRAM tilemap;
`01..FC` = wait that many frames, then the same copy; `FE ptr(2)` + copy (30:927A draws the number at ptr);
`FD addr(2)` jump; `FF` end. Strings are the ROM rectangles those copies read (133):
- `script` (34): scripts reached by `LDA #addr; JSL $29A1EA` (60 starts);
- `table` (87): copy ops elsewhere in bank $33 (scripts picked from tables, e.g. 29:B3FC `LDA $9286,X`, the 18
  callers without an immediate) whose rectangle reads a kana run of `tools/re_battle_text.py`;
- `scan` (12): runs nothing above reads, one row, geometry a guess: the victory line `0x140017` (bank $28 code), the
  bank-$2D mana/spell info screen (`0x16EF84+`; reader not found, maybe a field screen), `たれか？`/`たれを？`/
  `さくせんセレクト` (`0x19895C+`).
Write-back is in place with the same tile count (`battle_text.encode`): English rows split by `{nl}`, each <= w
tiles, <= h rows, padded with space tile $93; a 2-row rect (dakuten row + kana row) can hold two English rows.
Verified on the marker build (`work/qa/bcmd`): command label `bt_1987A5` (4x2) shows `87A5`; the spell-cast window
(30:ACB0) shows `spell 00 / The qui`. Excluded as data (`battle_text.EXCLUDE`): the name tile table and 5 short
odd-aligned matches. Single-tile particles (`bt_198045` の, `bt_1980E3` に, `bt_19D534+` し/ま/た) are pieces of
messages built at run time: English needs engine work there (moved to phase 8: `script/keep_jp.txt`).
Coverage (`tools/debug/battle_cover.py`, routes `tools/debug/battle_routes.tsv`): the command, orders sub-command
(まほう/ねらう/アイテム/そうび: only the selected label is drawn, so left/right before A picks it), who/what/whom
prompts, target frames, item descriptions (5 x n box right of the 2-column item list) and some item-use messages
are read in game. Not reachable from a new-game state: the 19E09C-19FABE family and 16EF84+ (mana names, spell
power/range labels, spell effect lines, "need more mana"/"max MP too low" boxes: the magic synthesis screen of the
magic healers, E4 06/07, which needs mana and money), the other party members' names (198926/36/46: needs a
party), status-effect messages 1D82xx and most use messages (need a damaged or afflicted party).
The synthesis family's scripts are started from bank-29 code `29:D4xx-E8xx` (`LDA #script; JSL $29A1EA` at
29:D50D, D8BF, D8E2, DA4D, DA63, DAA8, DC15, E7E8; state bytes `$1872-$18E5`, e.g. `$187A/$187B/$187C` gate the
29:D8BF box). None of it runs in the magic-healer flows E4 06 00/01/02 and E4 07 01 (`exec_log.lua`, run
`work/qa/syn5`: those scripts only offer heal yes/no, then pick a member). Next: find the entry (no JSL/JML or word
table points into 29:D420-D42B; look for a `JMP ($xxxx,x)` table in bank 29 or a PEA/RTL dispatch) and which
script or item (the 魔宝石 "magic gem" of `b04_C635`) opens it.
The spell info column right of the battle magic window (いりょく/しゃていきょり/MP, garbled "&:uま" by the
lowercase tiles) is not read from any ROM rect: 29:C910/CD7C read only the layout tables at `0x198E7B` and
`0x198F57` (destination lists), so its labels are tiles from a decompressed block in WRAM (phase 8, with the
battle status names). `tools/lua/bank_reads.lua` (every distinct address read in one bank) found this where
`snes_romreads.lua` (one line per PC) hid the copies.
The battle command label たたかう is drawn with the hiragana tiles that now hold English lowercase: it reads "uukf"
in the 4 MB build until phase 8 redraws it.

## Battle VWF (2026-11-24, D19; `tools/bvwf.py`, asm `bvwf_rect`)
Battle layout (ppu dumps `work/qa/bvwf0`): BG1 chr `$5000` map `$7400`, BG2 chr `$2000` map `$7800`, BG3 chr `$6000`
map `$7C00` (VRAM words). BG3 tilemap shadow **`$7E:B800`** (32 x 32 words), uploaded by the NMI VRAM queue
**2A:989A**: ring of 64 descriptor pointers at `$11EB`, head `$11E7`, tail `$11E9`, descriptors (VRAM word, 24-bit
source, size) read with DB = `$28`, so they live in bank `$28` or low WRAM; 30:F28C queues the tilemap (`$28:F44D`,
once per frame through `$1512`). BG3 tiles in use during battle: `$001-$119` (battle font), `$180-$1FC` (status
stream), so **`$11A-$17F` (102 tiles) is the VWF canvas** (`$1FD-$27F` look free too, unused so far). WRAM
`$7F:D800-$7F:E0EF` (zero in every field and battle dump; the largest script block ends at `$7F:37D7`): canvas shadow,
owner table, render buffer, state.
Hooks: 29:A278 (window-script copy loop, ROM sources only), 30:F242 (7-byte rect records: escape messages), 3C:8057
(victory line, rows 3-4), 30:AE2E (item-found line, rows 11-12). Typed messages (`battle_text.COLUMN_MSGS`) copy the
message so far from column 0 on every op, so the run is redrawn as it grows. The renderer splits each row into runs
(single spaces inside, two spaces / non-text tile / digit end one), draws a run at its first cell from the bold 8x8
glyphs trimmed to their ink (+1 px, space 4 px), and points its cells at canvas tiles allocated next-fit; a tile is
free again once its cell shows something else, so windows need no bookkeeping. Changed tiles go up in 16-tile chunks
through the queue (descriptors `$28:FC08`, zero filler in the original). Full canvas: the run keeps its fixed tiles.
Not drawn proportionally: rects copied from WRAM (names/numbers built by code), BG3 text drawn by other code.
