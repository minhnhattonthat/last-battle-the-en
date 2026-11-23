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

Canvas notes: each text line owns 32 VRAM tile columns (256 px) at `$6600 + line * $200`; text past 256 px wraps
into the line's bottom-row tiles and the next line (seen in the ruler shot), so overflow shows as garbage, not a clip.
The longest Japanese dialogue lines are 18 glyphs = 216 px, matching the box.

Still to measure (next session): the last line with the page-wait arrow; windowed messages (`menu_item` "who uses"
box, `svc_*` shop/inn boxes, battle message box, epilogue text on black in `credits`), place-name banner
(`place_*`, centred with leading spaces), item / spell name fields (menus, shop, battle), status-window name field.
