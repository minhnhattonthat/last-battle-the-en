# Box variants and width budgets (the width gate, phase 5)

Budgets are VWF pixels (`tools/font_en.py` ADVANCE) measured in-game from a ruler build
(`build.py --out build/ruler.sfc --qa "ID=..."`), never derived from the Japanese length. Each row says measured (with
the shot) or guess. The fit lint (phase 7) reads this table.

| Variant | Where | px per line | Lines | Status |
|---|---|---|---|---|
| dialogue | bottom box: NPC talk, events, name-entry prompt | 216 (screen x 24-239; canvas column 27+ is under the border) | 3, a 4th `{nl}` scrolls | measured: `work/qa/ruler/name_entry/final.png` (2026-11-23), `#` row ends at x 238 |
| BG3 name field | shop buy list (and other FEAA lists): item names | 8 characters (8x8 fixed tiles, upper and lowercase + `',.-!?&/:+` from `tools/font_bg3.py`); the shop row has room from x 24 to the price at x ~128 (13 tiles) once the cap is raised per screen | 1 | measured: `work/qa/bg3t/p00_0x4D_10_6/f002400.png` (2026-11-23, "Long gap", "Bad-Day!") |
| shop item description | right-hand box of the shop (`つかうと HPを 30ほど かいふく`) | ~5 tiles x 4 lines (8x8 BG3 tiles) | 4 | guess from `work/qa/shop2/p00_0x4D_10_6/f002400.png`: not extracted yet (BG3 tile-word strings in bank 04, see status) |
| staff roll | `credits` scene after the epilogue (`cr_*`, bank-02 renderer + `cr_glyph` VWF) | 192 (screen x 32-223) | 5 slots of 32 px (`{nl}` = next slot; the JP entries leave slot 1 blank) | measured: `work/qa/cr2/credits/f013500.png` (2026-11-23); a longer line wraps into the start of the next slot |

| place-name banner | `place_*` on room entry (bank-04 `b04_B3B0`...) | 144 (24 ruler digits, the 24th ends at the border) | 1 | measured: `work/qa/rb/banner.png` (2026-11-23, `build.py --qa b04_B3B0=<40-digit ruler>`); JP names are centred with leading spaces: centre English the same way (space = 4 px) |
| epilogue text | `ending` (white text on black, no box) | 216 (screen x 24-239, the dialogue canvas; a 37th ruler digit wraps as garbage into the next line) | free | measured: `work/qa/epi/ending/f013020.png` (2026-11-24, `build.py --out build/qa_epi.sfc --qa "r320_0368=<40 digits>{nl}<40 W>"`) |
| shop / inn / healer talk | `svc_*` bottom box | 216, same box as dialogue | 3 | measured: `work/qa/ruler_tour/svc_00_00/final.png` (2026-11-24) |
| item-use message | `menu_item` > item > use: bottom box (`[b04_B2DA][b04_B9DA]` + item name) | 216, same box as dialogue | 3 | measured: `work/qa/mitem/p00_0x4D_10_6/f003060.png` (2026-11-24, items poked `@19CF:4342,@19D1:4544`) |
| field item list | `menu_item` item window, 2 columns (BG3 name field) | 11 tiles per column (x 95 to the next column at x 183); names capped at 8 until the per-caller cap | 1 | measured: `work/qa/mitem/p00_0x4D_10_6/f002820.png` (2026-11-24) |
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

Still to measure: BG3 name fields per caller once the per-caller cap exists (shop list 13, field item list 11;
status window, equip, battle item list), the description boxes (5 tiles x 4 lines, needs engine work).
