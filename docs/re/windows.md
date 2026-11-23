# Box variants and width budgets (the width gate, phase 5)

Budgets are VWF pixels (`tools/font_en.py` ADVANCE) measured in-game from a ruler build
(`build.py --out build/ruler.sfc --qa "ID=..."`), never derived from the Japanese length. Each row says measured (with
the shot) or guess. The fit lint (phase 7) reads this table.

| Variant | Where | px per line | Lines | Status |
|---|---|---|---|---|
| dialogue | bottom box: NPC talk, events, name-entry prompt | 216 (screen x 24-239; canvas column 27+ is under the border) | 3, a 4th `{nl}` scrolls | measured: `work/qa/ruler/name_entry/final.png` (2026-11-23), `#` row ends at x 238 |

Canvas notes: each text line owns 32 VRAM tile columns (256 px) at `$6600 + line * $200`; text past 256 px wraps
into the line's bottom-row tiles and the next line (seen in the ruler shot), so overflow shows as garbage, not a clip.
The longest Japanese dialogue lines are 18 glyphs = 216 px, matching the box.

Still to measure (next session): the last line with the page-wait arrow; windowed messages (`menu_item` "who uses"
box, `svc_*` shop/inn boxes, battle message box, epilogue text on black in `credits`), place-name banner
(`place_*`, centred with leading spaces), item / spell name fields (menus, shop, battle), status-window name field,
staff roll (bank-02 renderer, not hooked yet).
