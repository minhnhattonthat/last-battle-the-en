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
pattern of mm+1 bytes. The decoder runs while the source < start + length - 1.

## Battle messages and screens (not extracted yet)
BG3 tile words with palette bits (`$20xx`/`$21xx`, tiles >= $100 are kanji or two-row pieces) inside window
scripts run by 29:A1EA (ops like `01 <dest> <src> 08 02`, see `$33:D4A1`). `tools/re_battle_text.py` lists 264
runs / 3171 tile words in banks $28-$33 (`work/qa/battle_text.txt`): victory lines (`0x140017`
"を やっつけた！！"), the mana / spell info screens in bank $2D (`0x16EF44+`: ほのおのマナ, けんえいすう...), battle
equip/status labels in bank $30 (`0x186344+`: そうびできる ぶきを もっていません, こうげき, すばやさ...). Many runs
are blank-tile padding. Next: walk the window-script format of 29:A1EA, find how each run is reached (pointer or
inline), add a `battle` kind (tile words + palette) with marker text and far jumps or relocation.
The battle command label たたかう is drawn with the hiragana tiles that now hold English lowercase: it reads "uukf"
in the 4 MB build until phase 8 redraws it.
