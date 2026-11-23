# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3. Identity build next (phase 2 debug tool done 2026-11-23). Last build: none yet.
- **Done:**
  - Step 0 and phase 1 (recon): see `docs/re/` (encoding, font, LZ, pointers, control codes, room format, bank-04
    text map, byte-encoded names, free space, static graphics sweep).
  - **Phase 2 (debug tool), `docs/re/debug.md` has the RAM map, save format, story variants and ending:**
    - `tools/debug/warp.lua`: cold boot -> any room (rewrites the game's map-change request at the first
      `00:964C`), READY when entered, then scene keys. `ops:<hex>` runs script bytes from `$7EFF00` (shops, inns,
      healers via E4), `@ADDR:VAL` pokes at READY (`@1DDF:00gg` = forced battle), cheats `god`/`win`/`noenc`,
      `credits` (skips the endless sound wait after "Fin" so the staff roll plays). Scene rooms `title` (keys from
      power-on) and `load` (load FILE1 from the title), pokes word `sav=<file>` (run_scenes passes `--sav`).
    - `tools/debug/scenes.tsv` (113 scenes; core rows from `tools/debug/gen/core_rows.py`, rewrite with
      `gen/regen_scenes.py`): title, name entry, newgame, overworld, 7 field menus + tactics/formation, overworld
      menu, camp/save flow (files, confirm, done), quit, title_load (load screen), load_file1, stress_money,
      battles/victory/wipeout, 33 place_*, 37 svc_*, 10 variant_ec* + 3 variant_6f_* (story-variant room blocks
      29-42), ending (epilogue + Fin), credits (staff roll).
    - `tools/debug/run_scenes.py`: every scene reaches READY from a cold boot with shots in `work/qa/scenes/`
      (see the commit message for the last full run).
    - **Saving:** overworld menu > camp icon > セーブする. `tools/debug/save.py` (dump/edit: money, flags, room/x/y,
      any byte the save stream holds; checksum, backup copy and load-screen header rebuilt), `tests/test_save.py`
      (bit packer, descriptor table vs ROM, byte-exact round trip of the game-written fixture
      `tests/fixtures/base_file1.srm`). `tools/debug/make_saves.py` regenerates `work/saves/` (base save written by
      the game in the save_done scene; stress saves edited from it) and loads each edited save in game, asserting
      room and money in WRAM (`save_check.lua`): stress_money (9,999,999) loads clean, no corruption message.
    - Probes: `tools/lua/{exec_log,pc_sample,skip_apu_wait,...}.lua`; `tools/debug/probe.py` ad-hoc warps.
- **Next:**
  1. **Phase 3 identity build** (`references/pipeline.md` §Identity): unpack (LZ blocks, room/top tables, text) and
     repack with no edits; the rebuilt ROM must be byte-identical (a test). `build.py` + `rom.sha1` check first.
  2. Carried to phase 4: 18 unreferenced text runs (`script_dis.py --gaps`); enemy names still not found; menu
     labels and window texts are bank-04 BG3 tile words (file `0x20400-0x22300`); credits text `0x16245-0x16877`
     (pointer table `02:E215`, 24 entries).
  3. Carried to phase 8: graphics tour (graphics.md "Tour half": VRAM dump per scene, classify every Japanese
     element as font text or tiles; the scene list now reaches every screen it names); stress saves for full party,
     all items/spells and long names (`save.py` can write them once the record fields are mapped: record widths
     `03:FA3E`, items live in the character records, "クルト は アイテムを もっていません"); re-run
     `tools/lua/trap_reads.lua` over the scene runs before using free space.
  4. Chapter 4 recap (room 198 NPC talk `$7F:015A`) has no scene: talking to that NPC needs its position; text
     coverage will flag it if missed.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
