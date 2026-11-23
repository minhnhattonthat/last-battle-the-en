# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| tools/font_en.txt | drawn by the repo owner for bounty-sword-en (2026-11-22), copied 2026-11-23 | same as repo | yes | all English text: the VWF (`asm/vwf.asm`, `docs/re/vwf.md`) | header comment only |
| tools/font_bg3.py | drawn for this repo (2026-11-23), styled after the game's own 8x8 capitals | same as repo | yes | lowercase and punctuation in the 8x8 BG3 font (list names, later menu labels) | new glyphs |
