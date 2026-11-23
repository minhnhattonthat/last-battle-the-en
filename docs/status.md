# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build in progress (VWF, far jumps, staff roll and item/spell name escapes
  work; BG3 font has English lowercase; per-screen BG3 name caps, party names / name entry, extracting the BG3
  tile-word strings (shop descriptions), the rest of the width gate and the marker tour left). Builds are 4 MB with `asm/vwf.asm`: `build/marker.sfc` (`build.py --marker`) boots (smoke
  ok) and reaches name_entry, newgame, menu_item, place_00, svc_00_00, battle_win, variant_ec01 (`work/qa/marker2`)
  and the staff roll (`work/qa/cr1`) with `[id]` markers.
- **Done:**
  - **Phase 5, session 2026-11-23 (3):** 8x8 BG3 font gets English lowercase + `',.-!?&/:+` (`tools/font_bg3.py`,
    drawn over hiragana tiles `$25-$48` of LZ block 319; `insert.bg3_table` maps them; test in `tests/test_vwf.py`).
    Shop list shows mixed case: `work/qa/bg3t/p00_0x4D_10_6/f002400.png`. Chose fixed 8 px tiles over a BG3 tile
    VWF: BG3 chr has no free tiles past `$BF` (`docs/re/vwf.md` §Names). Found the shop description source (below).
  - **Phase 5, session 2026-11-23 (2):** staff roll: bank-02 renderer hooked (`cr_glyph` VWF, `cr_fetch` far jumps),
    width 192 px x 5 slots measured. Item/spell names: escape `kind, n` in the record + English table at `$FC:8000`
    read by both name decoders (01:FEE3 glyph words, any length; 01:FEAA BG3 tiles, capped at 8): `docs/re/vwf.md`
    §Names, `insert.NameTable`, `tests/test_vwf.py::test_name_escape_and_table`. Marker build now marks names too.
  - **Phase 5 so far** (`docs/re/vwf.md`, `docs/re/windows.md`):
    - VWF in `asm/vwf.asm` (asar 1.91 copied to `tools/asar/`, gitignored): hooks 01:B89B/B8C9/B859/B13C on the
      bitmap glyph renderer; Japanese still draws at 12 px through it (shots identical to the original). English
      font `tools/font_en.txt` (own design, reused from the owner's bounty-sword-en project; add its row to
      `docs/fonts.md`), words `$0800+ASCII` (`textcodec.EN`).
    - Relocation without moving anything: strings keep their slot; longer English goes to `0x300000+` behind a far
      jump (new script word `$F700` + 24-bit address, hooked in the VM dispatch 01:BA96 and the menu string fetch
      01:B485) and jumps back. Verified with the bank-04 name prompt moved. Room blocks never grow (E5 reloads them
      at `$7F0000`, `$7F:4000` is used by other code).
    - `build.py --qa ID=TEXT` (ruler/QA overrides), `--marker`; `asm=False` keeps the identity build 2 MB.
    - Width gate: dialogue box = 216 px x 3 lines (measured, ruler build).
  - **Phase 4 (extract):** `tools/extract.py dump` -> `script/*.json` (205 files, 2591 strings, 184.6k JP chars;
    23 unreached runs kept with `"reached": false`), codec `tools/textcodec.py`, write-back `tools/insert.py`
    (called by `build.py`, same-size only for now). `tests/test_extract.py`: roundtrip of every string, script/ in
    sync with a fresh extraction, coverage (every walked glyph and every text run in blocks, bank 04 text area and
    credits inside a string or a known data range, no overlaps), build splices edits and refuses size changes.
    Details and token names: `docs/re/text.md` §Extraction. Write ranges for raw text added to `tools/ranges.txt`.
  - **Phase 3 (identity build):** `build.py` (rom.sha1 check -> `tools/blocks.py` unpack -> repack -> romdiff with
    the write log `build/writes.txt`; writes only inside `tools/ranges.txt`). `tools/lz.py compress` (optimal parse,
    0.5% smaller than the original). `tests/test_identity.py`: no-edit build == original; every block recompressed
    and moved decodes through every slot; one edited block. `build.py --recompress` (all 324 blocks re-encoded and
    moved) reaches all 113 debug scenes (`work/qa/scenes_recomp`). `tools/debug/compare_runs.py` pairs final frames
    of two runs: scene runs are not frame-deterministic (two runs of the original differ in 20 scenes), and the
    relocated build's extra differences were animation phase and different random encounters in the mash-A
    `variant_*` scenes (decompression timing moves the RNG), checked by eye.
    Bank-04 script and other raw text are passed through untouched until phase 4 adds writers for them.
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
  1. **Finish phase 5** (done-when: marker ROM boots, every text box shows its id, non-text strings excluded, every
     box variant measured):
     - **BG3 name fields** (01:FEAA path; `docs/re/vwf.md` §Names): lowercase done; English names are still capped
       at the caller's count (8; 01:FE59 item records = shop list, 01:FE3B character names, both `LDA #$0008`).
       The shop row has room for 13 tiles (x 24 to the price at ~128; check the longest price). Raise the cap for
       English only (never the JP loop, which reads `$6D80` past its 8 bytes): in `nm_feaa`, pick the cap from the
       return address (a small table: caller -> tiles), after finding every screen each caller serves (inventory,
       equip, status, battle) and measuring its field. Shop probe: `tools/debug/probe.py OUT "0x4D 10 6 30 -;6 a;60
       -;6 a;60 -;6 a;60 -;6 a;90 -;6 a;90 -;6 a;90 -;6 a;120 -|01E402|-" --rom build/bg3t.sfc --frames 2600`
       (list at ~f2400; build it with `build.py --marker --out build/bg3t.sfc --qa item_42=...`).
     - **Party names / name entry**: names stay plain bytes (`$30-$39`, `$41-$5A` are already ASCII); lowercase
       bytes `$61-$7A` map to kana. Remap both maps (`0x23053` glyph words -> `$0861+`, `0x22EAB` BG3 tiles) for an
       English grid; the grid order is the map order (`docs/re/graphics.md`). Default names (クルト, メイ `b04_B2E2`).
     - **Unextracted text**: the shop item description box (つかうと HPを 30ほど かいふく) is BG3 tile words in
       bank 04: `つかうと` at file `0x22331`, `かいふく` at `0x21A82` (tile word = `$04:AEAB` map of the byte code; the
       same form as the menu labels in `0x20400-0x22300`, which text.md left for phase 8). These are real text:
       extract the tile-word strings (a BG3 tile codec: tiles -> kana via the byte map, English via
       `font_bg3.TILE` + capitals/digits), find their pointers/readers, mark them in the marker build, and measure
       the box (~5 tiles x 4 lines looks too small for English: plan engine work, e.g. a wider box or the VWF canvas).
     - `b04_B2E2` (メイ, 4-byte slot, pointer `0x232D4`): too short for a far jump; move it by its pointer into
       dead space of another bank-04 string (marker build writes the id tail meanwhile).
     - Width gate for the variants listed in `docs/re/windows.md` (ruler builds via `--qa`); the page-wait arrow.
     - Tour the marker build over all scenes (`run_scenes.py build/marker.sfc`) and list any Japanese left (text not
       extracted) and markers in odd places (non-text): mark those `data` in `script/`.
     - Tests so far: `tests/test_vwf.py` (font, EN codec, far-jump fit); add one that boots nothing but checks the
       marker build's writes stay in `tools/ranges.txt` (build.py already refuses others).
  2. The 23 unreached runs (`"reached": false`): check at runtime with a ROM-read probe or textcoverage; menu
     labels and window texts are bank-04 BG3 tile words (file `0x20400-0x22300`) and tile rows `0x22CA7`:
     graphics text, not in `script/`; enemy names not shown in battle (confirm in the phase-8 tour).
  3. Carried to phase 8: graphics tour (graphics.md "Tour half": VRAM dump per scene, classify every Japanese
     element as font text or tiles; the scene list now reaches every screen it names); stress saves for full party,
     all items/spells and long names (`save.py` can write them once the record fields are mapped: record widths
     `03:FA3E`, items live in the character records, "クルト は アイテムを もっていません"); re-run
     `tools/lua/trap_reads.lua` over the scene runs before using free space.
  4. Chapter 4 recap (room 198 NPC talk `$7F:015A`) has no scene: talking to that NPC needs its position; text
     coverage will flag it if missed.
- **Open bugs:** none.
- **Waiting on the user:** non-blocking: BG3 list names (shop list etc.) use a fixed 8 px font with lowercase rather
  than a VWF, since BG3 has no free tiles for one; default kept, say if you want the bigger engine change.
