# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build in progress (VWF, far jumps, staff roll, item/spell name escapes,
  BG3 menu strings, spell ranks, the English name-entry grid, battle names, the battle font and battle tile text
  done; battle-window tour started (20/133 ids seen); left: the rest of the battle tour, per-caller BG3 name caps,
  description boxes, the rest of the width gate, a full re-tour).
  Builds are 4 MB with `asm/vwf.asm`: `build/marker.sfc` (`build.py --marker`) and `build/lastbattle_en.sfc` boot
  (smoke ok, 2026-11-23 session 8).
- **Done:**
  - **Phase 5, session 2026-11-23 (8):** battle coverage tool: `tools/debug/battle_cover.py OUT` runs the routes in
    `tools/debug/battle_routes.tsv` on `build/marker.sfc` with `tools/lua/rect_reads.lua` (logs the first CPU read of
    each `script/battle.json` rect) and writes `OUT/cover.tsv` (id, route, frame). Run `work/qa/bcov2`: 20/133 read:
    command labels `87A5/B5/C5/D5` (A opens "COMMAND", the 4-icon menu is up ~120 frames later; icons fight/orders/
    tactics/run), magic `8841`, tactics prompt `88A6`, `8916`, `895C` たれか, `89AE` さくせんセレクト, `91EC`
    なにを, `920D/923D/926D` (target frames), `9310` たれに, victory `140017`, particles; markers seen in
    `work/qa/bcov2/k1.png`. Garbled still: the spell info column right of the magic window (`&:uま`, `MP`), not in
    battle.json (tiles drawn by other code: find its source). Page-wait arrow measured: below line 3, no width cost
    (`docs/re/windows.md`). `b04_B2E2` (メイ, 4-byte slot) now moves into a bank-04 pool `0x27F00-0x27FFF` and its
    pointer `0x232D4` is rewritten (`insert.BankPools`, test `test_bank_pool_repoints_short_slot`); its screen is
    not yet seen in game, and the pool ($FF padding) still wants a `trap_reads.lua` pass.
  - **Phase 5, session 2026-11-23 (7):** battle tile text extracted (`docs/re/battle.md` §Battle messages):
    window-script format of 29:A1EA decoded; `tools/battle_text.py` -> `script/battle.json` (133 in-place rects:
    34 direct scripts, 87 table-reached script ops, 12 scanned runs), roundtrip in `test_roundtrip`, marker and
    English encode (`test_battle_text_rects`), write ranges in `tools/ranges.txt`. Marker build verified in battle
    (`work/qa/bcmd`): command label `87A5`, spell-cast window `spell 00 / The qui` (first time seen in game).
  - **Phase 5, session 2026-11-23 (6):** battle names (`docs/re/battle.md`): enemies (93) and tactics (8) extracted
    (`script/enemies.json`, `script/tactics.json`, FF-padded fields, `"field"` = where the escape goes); hook 29:B2B6
    (`bt_name`) draws English escapes as two 8-tile rows (`insert.battle_rows`: names up to 16 chars, split at a
    space); default battle spell slots `0x19D3F1` become spell escapes; ASCII party-name bytes in the battle byte
    tables. The battle BG3 font is its own copy in a **battle LZ** (`tools/blz.py` decode/encode, re-encoded in
    place with the English tiles by `font_bg3.battle_patch`). Marker build shows "enemy 07 / The qui" in the enemy
    window (`work/qa/mbat3`). Survey of battle message text: `tools/re_battle_text.py` (264 runs). Tests:
    `test_battle_rows`, `test_battle_name_table_and_bytes`, `test_battle_lz_roundtrip_and_font`.
  - **Phase 5, session 2026-11-23 (5b):** English name entry (`insert.name_entry`, `docs/re/vwf.md` §Name entry):
    15-row grid A-Z / a-z / digits / punctuation, ASCII name bytes in both byte maps, row count patched in 5 places;
    new scene `name_type` types "ABbc2" (`work/qa/ne2`); test `test_name_entry_grid`.
  - **Phase 5, session 2026-11-23 (5):** BG3 tile strings extracted: `script/menus.json` (260, kind `bg3`, codec
    `textcodec.bg3_jp/bg3_en`, `docs/re/text.md` §BG3 strings), written back by `insert.apply` (far jumps through
    the VM), marked in the marker build (`addr:` + filler, same tile count). Marker tour of 22 menu/save/shop/battle
    scenes (`work/qa/bg3m`): prompts, yes/no, stereo/mono, status labels, save/load prompts show their ids. Spell
    names with rank in character records (`insert.spell_refs`, asm ` RANK`): "Fire A" in `menu_magic`.
    Tests: `test_bg3_strings`, `test_bg3_marker_keeps_tile_count`, `test_spell_rank_records`.
  - **Phase 5, session 2026-11-23 (4):** marker tour of all 113 scenes (`work/qa/marker_tour`, sheets of the final
    frames `work/qa/mt_sheets/sheet*.png`): every scene reached, dialogue, shop/inn/healer talk, place banners,
    ending and variants show `[id]` markers. **Japanese / garbled left** (text not extracted yet), see Next 1a-1c.
    `build.py --ruler` (`insert.ruler_text`, test `test_ruler_text`) + ruler tour (`work/qa/ruler_tour`, 30 scenes):
    place banner measured 144 px, epilogue >= 192 px (`docs/re/windows.md`). `tools/lua/stack_log.lua` (return
    addresses at entry to a routine, for the per-caller BG3 caps). Size check: 127k JP glyphs ~ 550 KB of English
    words at 2.2 letters per glyph, `TEXT_AREA` is 896 KB (fits; watch it in phase 7).
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
     box variant measured). Left:
     - **1a. Battle-window marker tour** (started, `battle_cover.py`, 20/133 read): add routes to
       `battle_routes.tsv` for the 113 ids still unread (`work/qa/bcov2/cover.tsv` lists them: items in battle
       `185xxx` descriptions, equip/status, run, mana screen `16EFxx`, the `19E5xx-19EBxx` message family,
       `1D82xx`); deeper menus need longer key chains after the command menu, other encounters (`@1DDF`), and a
       party with items/spells (stress save). If whole families never fire a CPU read, check for DMA from ROM.
       Old notes: with pokes
       `god,@1DDF:0053` from room 0x00 40 30, READY is f2149 and the gray command menu is up at ~f3390, so keys
       start with `1100 -` (`tools/debug/probe.py work/qa/bcmd --rom build/marker.sfc --frames 4400 "0x00 40 30 1100
       -;6 right;30 -;6 a;60 -;6 a;200 -|-|god,@1DDF:0053"`). The battle
       auto-fights first: menus need the right moment. Confirm or fix the 12 `scan` geometries (one row, guessed):
       find the reader of `0x140017` (victory), `0x16EF84+` (mana screen, bank $2D), `0x19895C+` with
       `snes_romreads.lua`. Rank form of the spell-cast window still unseen. The 8-byte table at `0x182C57`
       (クルト, メイ, ボルグ, レジーナ) had no reader in `battle_field`; find its user. Enemy names `enemy_40` /
       `enemy_69` use two-row kanji bytes: shoot them in battle for the translator (`@1DDF` picks the encounter).
     - **1b. Re-run the full marker tour** (113 + `name_type`) on the current marker build and list what is still
       Japanese (`work/qa/mt_sheets` is from before the BG3 strings).
     - Name entry opens with rows `56789` / `: +` above the cursor row `ABCDE` (the view shows 2 rows before row 0,
       as the kana grid did): consider reordering `insert.NE_GRID` so the first view starts on letters.
     - **BG3 caps for FA inserts**: names inserted into BG3 strings (FA0F/FA18/FA2B/FA2F/FA42) all reach 01:FEAA
       through the same handlers (FA2F -> FA8A -> FE09, return FE1E/FA8F), so a return-address cap table can't tell
       screens apart there; key on the FA op instead (VM pointer `$10` - 2) or let translators lay out rows for an
       8-tile name. Shop list (FE76 <- F3C2) and character names (FE55 <- EF07) can use the return-address table.
     - **BG3 name fields** (01:FEAA path; `docs/re/vwf.md` §Names): lowercase done; English names are still capped
       at the caller's count (8; 01:FE59 item records = shop list, 01:FE3B character names, both `LDA #$0008`).
       The shop row has room for 13 tiles (x 24 to the price at ~128; check the longest price). Raise the cap for
       English only (never the JP loop, which reads `$6D80` past its 8 bytes): in `nm_feaa`, pick the cap from the
       return address (a small table: caller -> tiles), after finding every screen each caller serves (inventory,
       equip, status, battle) and measuring its field. Shop probe: `tools/debug/probe.py OUT "0x4D 10 6 30 -;6 a;60
       -;6 a;60 -;6 a;60 -;6 a;90 -;6 a;90 -;6 a;90 -;6 a;120 -|01E402|-" --rom build/bg3t.sfc --frames 2600`
       (list at ~f2400; build it with `build.py --marker --out build/bg3t.sfc --qa item_42=...`).
     - **Description boxes** (item/spell descriptions in the shop and spell screens, now `bg3_A3xx`-`bg3_ACxx` in
       `menus.json`): 5 tiles per line x 4 lines of 8 px fixed tiles, far too small for English. Plan engine work
       (wider box via the window op, or draw them through the VWF canvas) and measure the result.
     - Width gate still to measure (`docs/re/windows.md` "Still to measure"): the epilogue right edge, the item-description box (`common`/bank-04 descriptions, `menu_item` > item > info),
       battle message box, BG3 name fields per screen (`stack_log.lua --var "ADDRS='01FEAA'"` over the menu, shop
       and battle scenes gives each caller; then the per-caller cap table in `nm_feaa`).
     - No marker showed in an odd place in the tour (no non-text found yet); re-check after 1a.
     - Tests so far: `tests/test_vwf.py` (font, EN codec, far-jump fit); add one that boots nothing but checks the
       marker build's writes stay in `tools/ranges.txt` (build.py already refuses others).
  2. The 23 unreached runs (`"reached": false`): check at runtime with a ROM-read probe or textcoverage; menu
     labels and window texts are bank-04 BG3 tile words (file `0x20400-0x22300`) and tile rows `0x22CA7`:
     graphics text, not in `script/`; enemy names not shown in battle (confirm in the phase-8 tour).
  3. Carried to phase 8: battle status party names (tiles in the second battle LZ stream, `docs/re/battle.md`), the
     battle command label たたかう (now garbled by the lowercase tiles); graphics tour (graphics.md "Tour half": VRAM dump per scene, classify every Japanese
     element as font text or tiles; the scene list now reaches every screen it names); stress saves for full party,
     all items/spells and long names (`save.py` can write them once the record fields are mapped: record widths
     `03:FA3E`, items live in the character records, "クルト は アイテムを もっていません"); re-run
     `tools/lua/trap_reads.lua` over the scene runs before using free space.
  4. Chapter 4 recap (room 198 NPC talk `$7F:015A`) has no scene: talking to that NPC needs its position; text
     coverage will flag it if missed.
- **Open bugs:** none.
- **Waiting on the user:** non-blocking: BG3 list names (shop list etc.) use a fixed 8 px font with lowercase rather
  than a VWF, since BG3 has no free tiles for one; default kept, say if you want the bigger engine change.
