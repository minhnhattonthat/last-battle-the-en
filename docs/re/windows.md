# Box variants and width budgets (the width gate, phase 5)

Budgets are VWF pixels (`tools/font_en.py` ADVANCE) measured in-game from a ruler build
(`build.py --out build/ruler.sfc --qa "ID=..."`), never derived from the Japanese length. Each row says measured (with
the shot) or guess. The fit lint (phase 7) reads this table.

| Variant | Where | px per line | Lines | Status |
|---|---|---|---|---|
| dialogue | bottom box: NPC talk, events, name-entry prompt | 216 (screen x 24-239; canvas column 27+ is under the border) | 3, a 4th `{nl}` scrolls | measured: `work/qa/ruler/name_entry/final.png` (2026-11-23), `#` row ends at x 238 |
| BG3 name field | item names in the lists drawn by 01:F3C0 (8x8 fixed tiles, upper and lowercase + `',.-!?&/:+` from `tools/font_bg3.py`) | per list, asm `nm_icap` (test `test_item_name_fields_fit_their_windows`): **9** in the shop buy list FA3C (the price follows the name: at 12 it leaves the window), FA11, FA16, FA09, FA4B; **9** in the field item windows FA0E since phase 7 (was 8: 2 columns of space + name in 18 tiles; widened to 20/21, see "field item list") | 1 | measured 2026-11-24: `work/qa/cap/p00_0x4D_10_6/final.png` (item window, 8), `work/qa/cap/p01_0x4D_10_6/final.png` (shop, 9), `work/qa/cap2` (shop at 12: price pushed out); FA11/FA16/FA09/FA4B by the test only (screens below) |
| item description | `menus.json` `box: desc_item` (29 strings, `$A331-$A8EA` minus the `$A6ED` stat template): the same strings show in the shop (right box) and the field item menu (left box) | **6 tiles** (8x8 BG3, fixed): the item menu box is 6 wide (a 7th tile sits on the border); the shop box is 8 | **7** (16 px pitch; both boxes) | measured: `work/qa/desc/p00_0x4D_10_6/final.png` (shop, 8 x 7) and `work/qa/desc2/item_z.png` (item menu, 6 x 7), 2026-11-24, ruler build `build/qa_desc.sfc` (every description = `1234567890AB{nl}abcdefghijkl{nl}...` 7 lines). `$A779` starts with a `{FA51}` spell name (8 tiles) and can't fit 6: give it its own line and accept a cut, or shorten (phase 7) |
| spell description | `menus.json` `box: desc_spell` (29 strings, `$A8EB-$AC9E`), magic menu left box: an effect string (2 lines) then a stats string (labels いりょく/きょり/はんい/かくりつ/じかん/レベル/ほすう/ＭＰ) whose values the game draws | **7 tiles** (an 8th is under the magic window); **label lines: tiles 0-3**, the value is drawn at tiles 4-5 (right-aligned, tile 6 free) | 4 (2 effect + stats; 16 px pitch, the stats string starts 8 px under the effect's 2nd line) | measured: `work/qa/desc/magic_z.png` (ruler) and `work/qa/desc3/z.png` (`build/qa_sp.sfc`: `bg3_A8EB=AAAAAAAA{nl}BBBBBBBB`, `bg3_A8FF=P.......{nl}R.......{nl}M.......`, values 18 / 5 / 3 land at tiles 4-5), 2026-11-24 |
| staff roll | `credits` scene after the epilogue (`cr_*`, bank-02 renderer + `cr_glyph` VWF) | 192 (screen x 32-223) | 5 slots of 32 px (`{nl}` = next slot; the JP entries leave slot 1 blank) | measured: `work/qa/cr2/credits/f013500.png` (2026-11-23); a longer line wraps into the start of the next slot |

| place-name banner | `place_*` on room entry (bank-04 `b04_B3B0`...) | 144 (24 ruler digits, the 24th ends at the border) | 1 | measured: `work/qa/rb/banner.png` (2026-11-23, `build.py --qa b04_B3B0=<40-digit ruler>`); JP names are centred with leading spaces: centre English the same way (space = 4 px) |
| epilogue text | `ending` (white text on black, no box) | 216 (screen x 24-239, the dialogue canvas; a 37th ruler digit wraps as garbage into the next line) | free | measured: `work/qa/epi/ending/f013020.png` (2026-11-24, `build.py --out build/qa_epi.sfc --qa "r320_0368=<40 digits>{nl}<40 W>"`) |
| shop / inn / healer talk | `svc_*` bottom box | 216, same box as dialogue | 3 | measured: `work/qa/ruler_tour/svc_00_00/final.png` (2026-11-24) |
| item-use message | `menu_item` > item > use: bottom box (`[b04_B2DA][b04_B9DA]` + item name) | 216, same box as dialogue | 3 | measured: `work/qa/mitem/p00_0x4D_10_6/f003060.png` (2026-11-24, items poked `@19CF:4342,@19D1:4544`) |
| field item list | `menu_item` item window (FA0E), 2 columns (BG3 name field) | **9** tiles per name since phase 7 (D18): both FA0E windows moved to x=0 and widened by 2 (`insert.WINDOW_HEADERS`: `0x2131A` 18 -> 20, `0x21F7A` 19 -> 21); the right border meets the portrait window at tile 22, so 9 is the most | 1 | measured: `work/qa/cap3/p00_0x4D_10_6/final.png` (field item window, 9 letters whole, 12 cut at 9), `work/qa/cap4` ("Use which item?" layout at x=8, cursor on column 2), `work/qa/cap5/sell.png` (shop sell list), 2026-11-24 |
| tactics list | `menu_tactics` > A (01:FE7A, `LDA #$0008` at 01:FEA3) | 8 tiles; the formation icons follow | 1 | measured: `work/qa/tac/p00_0x4D_10_6/final.png` (2026-11-24) |
| status values | `bg3_8F96` `{009E}` | the value is drawn right-aligned over the blanks before the op: keep the JP's blanks (lint in `batches.py`) | - | measured: `work/qa/p7/menu_status/final.png` ("Attack" lost its "k", 2026-11-24) |
| BG3 menu strings | `menus.json` (`bg3_*`): command lists, prompts, labels | the JP tile count: the window around them is a fixed size | per string | by construction (`test_bg3_marker_keeps_tile_count`); widening one is window work (phase 7) |
| battle rects | `battle.json` (`bt_*`) | `w` tiles of 8 px per row, `h` rows (the rect the window script copies; a 2-row rect holds two English rows) | `h` | by construction (`battle_text.encode` refuses overflow); 12 `scan` rects have guessed geometry |

Ruler build: `python -X utf8 build.py --ruler` (every text segment -> 6 px digits, the 10th/20th/30th digit is the decade,
as wide as the JP segment + 36 px: the full 40 digits for every string overflow `insert.TEXT_AREA`); tour with
`run_scenes.py build/ruler.sfc --out work/qa/ruler_tour --only ...`. A box wider than JP + 36 px needs a `--qa` line.

Canvas notes: each text line owns 32 VRAM tile columns (256 px) at `$6600 + line * $200`; text past 256 px wraps
into the line's bottom-row tiles and the next line (seen in the ruler shot), so overflow shows as garbage, not a clip.
The longest Japanese dialogue lines are 18 glyphs = 216 px, matching the box.

Page-wait arrow (measured 2026-11-23, `build.py --out build/qa_arrow.sfc --qa "top20_0016=Line one{nl}Line
two{nl}<36 digits>{page}End."`, scene `svc_06_00`, `work/qa/arrow/x.png`): the arrow is drawn centred *below* line 3,
so a full 216 px third line keeps its whole width; the `{page}` then scrolls the box one line ("End." on the new
line 3).

Item list window scripts (bank 04, header `xxyy hhww`: low byte of the second word = inner width in tiles; `F600` =
cursor tile, `0093` = space, `FE00` row end, `FF00` script end): FA0E `0x21320` (18) and `0x21F80` (19), FA11
`0x2139E` (21: cursor, space, name, space, cursor, space, name), FA16 `0x2160C` (10), FA09 `0x2112C` (9), FA3C
`0x21F10`, FA4B `0x21F44` (18). 01:F3C0 = FE59 (record name -> `$6C80` tiles, 01:FEAA) then B6FA, which pads with
`$93` until `$20` = start + count x 2 (it compares for equality: a name longer than the count never ends).

By construction (no shot needed): the lists behind FA11/FA16/FA09/FA4B get 9-tile names from their window-script
widths (`test_item_name_fields_fit_their_windows`); character names (01:FE3B) are capped at 8 tiles and the name
entry stores at most 8 bytes, so every name fits; battle item list rows are battle rects (`w` tiles).

Description boxes: no engine change. BG3 has no free tiles for a narrower font, and the list windows beside both
boxes already fill the screen width (item window 2 x (space + 8) tiles, shop list name 9 + price). The Japanese is
itself terse (4-5 kana per line); English writes to the budgets above (`box`/`max_tiles`/`max_lines` in
`menus.json`, test `test_description_boxes`). Ruling and the alternative: `docs/decisions.md`.
