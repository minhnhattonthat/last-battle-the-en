# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress. Last build: none yet (2026-11-23).
- **Done:**
  - Step 0 complete: MesenCE qa-1 in `tools/mesen/`, smoke boots the original (`tools/routes/boot.txt`), Start changes
    the screen, Lua probe logs, pre-commit rejects a failing test, guard hook blocks the `sed -i` canary (hook block
    in `.claude/settings.json` points at the marketplace path), `python tools/skill.py` prints the skill path.
  - Recon (see `docs/re/`): encoding (16-bit LE words, glyph = code-$300, controls >= $8000), font (0x107CF3,
    16x16 1bpp TL/TR/BL/BR, JIS-ordered subset, 1233 glyphs), LZ format + `tools/lz.py`, linear block pointers.
  - **Full glyph table**: katakana + 1066 JIS-ordered kanji + 35 credit-name kanji, every cell proofed by eye
    (`tbl/font_jp.tsv` -> `tbl/jp.tbl`, test: strictly JIS-increasing).
  - **Control codes**: every handler's argument layout (byte-granular, the stream is not word-aligned), table in
    `docs/re/text.md`. `tools/script_dis.py` walks all 323 room blocks + the common block from their headers with
    0 errors (`tests/test_script_dis.py`). Room header format (talk/search/step/flag lists) documented.
  - Top pointer table 0xD0000 mapped (`docs/re/compression.md`): rooms, extra rooms 29-42, common block 11, font 7.
- **Next (finish phase 1):**
  1. Script sources not yet walked: bank-$04 uncompressed script (entry `$04:B930` new game; `$04:B2FC` pointer
     table used by A4 lo>=$80; `$04:B64E/50/52` chest subs; `$04:DC57` table read by A0/A1), top-table blocks
     14-28 (18/19 plain text; 20-27 tables), and the 18 unreferenced text runs `script_dis.py --gaps` lists
     (probe with `tools/lua/romreads_addr.lua` whether anything reads them, else mark dead).
  2. Locate menus, item/spell/enemy names, battle text, name-entry grid, save screen (`romreads_addr.lua` per screen;
     needs the scenes; boot route reaches name entry). Record in `docs/re/text.md` §Where text lives.
  3. Graphics-text survey (`docs/re/graphics.md`): tour + static sweep of raw and decompressed graphics.
  4. Free-space trap test (candidates in `docs/re/compression.md`).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
