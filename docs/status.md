# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress (text, pointers, free space done; graphics static sweep left). Last build: none yet (2026-11-23).
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
  - Session 2026-11-23 (2): top-table entries 14-28 = shop/inn/healer scripts in the common-block format, all walk
    clean (`script_dis.py --top topN`, in the test). Bank-$04 text area mapped string by string (`docs/re/text.md`
    table: places, chests, item/spell messages, mana, stat-ups, item descriptions, equip templates, party names).
    **Item and spell names are a 1-byte encoding** (byte -> glyph word via the map at 0x23053, 01:FEE3), 8-char
    records: items at 0x24AD1/0x25201 (20-byte records), spells at 0x14E20F (9-byte). Credits at 0x16245.
    Free-space trap test: 0 reads of any candidate over boot + first room (`tools/lua/trap_reads.lua`), with a
    positive control; plan to expand to 4 MB for new data. Recon scanners: `re_textscan.py`, `re_names.py`,
    `re_dumptext.py`, `re_trap.py`, `re_chain.py`, `re_sweep.py`, `re_blocksheets.py`.
- **Next (finish phase 1):**
  1. **Graphics-text static sweep: sheets are rendered but not yet read** (`docs/re/graphics.md` §Static sweep).
     Codex review attempt failed (usage limit until 2026-11-26; script `work/sweep/run_codex.sh`, brief
     `work/sweep/codex_brief.md`). Read `work/sweep/blocks/snes4_*.png` (21) and `work/sweep/raw_*_snes2.png` (16)
     yourself in a fresh context, or first identify the graphics formats from a VRAM dump (name-entry screen,
     menu) with `vramfind.py` and read only the relevant blocks. Record each text graphic as a row in
     `docs/re/graphics.md`. The tour half of the survey (menus, battle, cards, ending) waits for the phase-2 debug
     tool: note that in graphics.md and then move to phase 2.
  2. Not found anywhere (raw or LZ, word or byte encoding): **enemy names**, menu command labels, save-screen labels.
     Probably BG3 tile strings like `0x22CA7` or graphics; find on screen in phase 2 with `romreads_addr.lua`.
  3. Carried to phase 4: the 18 unreferenced text runs `script_dis.py --gaps` lists (+4 in top15) live in LZ
     blocks (WRAM `$7F`), so a ROM-read probe can't see them; extract them anyway and check with `textcover`.
     The code that selects top entries 14-28 is not yet traced.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
