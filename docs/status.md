# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator: phase 7 done (build green with romdiff, `batches.py check` 0 problems incl. the
  new keep-list and `{009E}` rules, 40 tests; 3077/3085 translated, the 8 left are battle-only in
  `script/keep_jp.txt`). `build/lastbattle_en.sfc` smoke ok, 2026-11-24 session 19, sha1 489d308c.
- **Done:**
  - **Phase 7, session 2026-11-24 (19), phase closed:** D18 (replaces D10's 12-letter names): both FA0E field item
    windows moved to x=0 and widened by 2 (`insert.WINDOW_HEADERS`, asm `nm_icap` FA0E = 9), so every item list
    holds 9 tiles; tactics list stays 8 (01:FE7A). Fix batch b061: 90 item names fitted to 9 (real names first,
    abbreviations flagged in `docs/polish.md`), 6 tactics to 8 (`Power[FF]Attack` had printed "[FF]" as text), item
    info headers + r123_00A2 follow; item_05 "Estoc" (a shop clerk said "Bastard?"). 2-tile slots: shop Buy/Sell
    window moved whole to the bank-04 pool (`insert.MOVED_WINDOWS`, window-table word 0x202EE, range added),
    feather note + equip labels Wpn/Shld/Feet repointed (`insert.BG3_PTRS`). Status screen labels Atk/Def/Agi/Wis:
    `{009E}` draws its value over the blanks before it ("Attack" lost its "k"); lint added. `batches.py check`
    now fails untranslated entries not in `script/keep_jp.txt` (8 battle-only ids with reasons) and tokens in
    English names. Test `test_english_build_moves` builds the English ROM (romdiff) and checks the moves. Shots:
    `work/qa/cap3` (item window 9, shop Buy/Sell `shopcmd.png`), `work/qa/cap4` (use-item layout, cursor col 2),
    `work/qa/cap5/sell.png`, `work/qa/tac`, `work/qa/p7/menu_status`; 38 menu/shop/save scenes reached
    (`work/qa/p7s/finals*.png`). Next free fix batch: b062.
  - **Phase 6, session 2026-11-24 (18):** external phase-6 review (`.harness/reviews/last-battle-the-en-phase6.md`)
    Critical/Important fixed: honorific check on in `tools/batches.py` (D1, waivers for title+name; tests), 24 hits
    re-translated, 先生 = "Keukenhof-sensei"/"Sensei" (D12), "King of Guld" everywhere (b059); D12-D17 recorded.
    C1: a fresh full re-read of every pair b001-b049 found 3 more Important (dead Guld/yogurt pun `r095_03AE`,
    "smelling herbs" vs item Revive Herb `r123_00A2`, broken chant page `top21_057E`) plus 3 minors, fixed in b060;
    log in `docs/review-phase6.md` "Session 18". Check 0 problems, 39 tests; smoke ok. Next free fix batch: b061.
  - **Phase 6, session 2026-11-24 (17):** reviewer pass b009-b049 done (self-review, read-only pass per batch; codex
    quota out). Fix batches b055-b058: old castle official / Ritten / Gulva / Kroket / Ude old-man voices restored,
    Regina's "honored wizard", garbled Svart and stutter lines re-punctuated, "master of the true word" ->
    "true word-speaker" everywhere, "Lord Lidar" -> "Lidar-dono". Minors added to `docs/polish.md`. Build, check
    (0 problems, 36 tests) and smoke green. Next free fix batch: b059.
  - **Phase 6, session 2026-11-24 (16):** external review findings fixed: phase 6 reopened; `docs/style-reference.md`
    rewritten (voice table JP markers -> EN devices, paired examples, corrected Yaak Chief example); Yaak Chief's 16
    lines re-voiced (fix batch b051); "Cardinal-sama" -> Your/His Eminence; Beebo "Feben-sama"/"Kee kee!"; synopsis
    Mei (elf, sent by King Robert) and Beebo fixed; glossary: `-dono`, titles never take honorifics, D10 field widths,
    "Decisions from earlier batches" filled; `docs/polish.md` in `- [ ] id - note` form; `r118_06C1` tense;
    "Febennels' House" (b052). New tools: `tools/fixbatch.py` (fix batch from merged ids), `tools/pairs.py`
    (reviewer pairs files `work/review/bNNN.txt`). Reviewer pass: **b001-b008 reviewed** (rows in
    `docs/review-phase6.md`); fixes b053 (Eldar Elder voice), b054 ("true word-speaker" in r009 and r293). Fix
    batches so far: b051-b054 (next free: b055). Session ended at the context limit; resume at b009.
  - **Phase 6, session 2026-11-24 (15):** batches b016-b049 merged (Rudom, elves, hidden village, Yaak, retaking
    Silvel, Guld, ending, spells, tactics, shops); glossary terms Hiram, Falk, Heeg, Lime, Tiran and others;
    `docs/synopsis.md`, first `docs/style-reference.md`; a self-review (superseded, see `docs/review-phase6.md`).
  - **Phase 6, session 2026-11-24 (14):** batches b002 (battle windows: commands Atk/Cmd/Plan/Run, synthesis-screen
    boxes, spell effect lines, status messages; sleeping NPCs) and b006-b015 (spell info boxes, Eldar village and
    school, the rite, Silvel Castle defence, King Gustav's reveal that Kurt is the prince, secret passage, occupied
    Silvel, Ude war council, Febennels' house) merged. `tools/batches.py`: speaker pages (`Name{nl}"speech`) keep the
    name line and wrap the speech; per-page narration from the JP page; `{F600}` choice lines not indented; script
    controls ($C000+) have no width, `{FAxx}` inserts count 56 px. `tools/merge_batch.sh` (merge, build, check,
    commit). Glossary: Yuse, Mias, Queen, Glad, Mr. Keukenhof, Elder, Sol, Ettmiranshel, Fenamun, Chancellor,
    Cardinal Ketteri, Commander Gubbe, Second Guld Castle, Prison Island, birdmen, spell synthesis, Missive. Dropped
    from b002/b006 for phase 7 (see translator brief): 6 battle particles/fragments, 3 two-tile equip-slot labels.
    No visual check of the new speaker-page layout yet (phase 8 tours cover it; first scene to look at: `r000_066E`
    Konrad at the Eldar gate).
  - **Phase 6, session 2026-11-24 (13):** `tools/batches.py` (skill asset adapted: split/check/merge/show/fit; wraps
    dialogue pages to 208 px with the `"` indent, centres banners and menu lines, per-kind limits: dialogue 3 lines,
    banners 144 px, credits 192 px, BG3 tile caps + `MENU_CAP` list windows, battle rects via `battle_text.encode`,
    names (items/tactics 12 = D10, spells 8 + rank rows, enemies 2 x 8), slots under 5 bytes, glossary + Avoid).
    `check.py` runs `batches.py check` on all shipped English; identity tests build with `build(jp_only=True)`.
    `glossary.md` filled (rulings, style, ~60 names); `docs/translator-brief.md` (the loop, format rules, notes).
    Batches split b001-b049 (`work/tl/`, gitignored, same worktree). Merged: b001 (bank-04 names, banners, chest/
    item/stat messages, item descriptions, 23 battle rects), b003 (snoring NPCs, credits romanised, 91 enemies),
    b004 (items, menu prompts), b005 (commands, status templates, tactics, teleport list, 6x7 descriptions).
    D10, D11 added. `codex exec` is out of quota until 2026-11-26 (usage limit), so no codex review yet.
  - **Phase 5, session 2026-11-24 (12), phase closed:** description boxes measured with a ruler build
    (`build/qa_desc.sfc`, every description = 12-digit lines x 7): item descriptions **6 tiles x 7 lines** (field item
    menu box, `work/qa/desc2/item_z.png`; the shop box is 8 x 7, `work/qa/desc/p00_0x4D_10_6/final.png`), spell
    descriptions **7 tiles x 4 lines**, stat label lines tiles 0-3 with the game's value at tiles 4-5
    (`work/qa/desc3/z.png`). `extract.bg3_strings` now tags the 58 description strings with `box`/`max_tiles`/
    `max_lines` (`DESC_BOXES`; `$A6ED` equip stat labels excluded), test `test_description_boxes`. No engine change
    (D9, agent default: BG3 has no free tiles, list windows fill the screen; alternative = descriptions through the
    dialogue VWF in a bottom box). Width gate rows for FA lists, character names (8 = name-entry max) and battle
    rects recorded as by construction. A zero-MP poke at READY (`@190D:0000`) did not bring up the not-enough-MP
    battle message (routes dropped).
  - **Phase 5, session 2026-11-24 (11):** marker re-tour `work/qa/marker_tour2` reviewed at full size (final frames
    of all 114 scenes, sheets rebuilt with `sheet.py --div 1 --cols 4 --max 12`): every dialogue, menu, shop, save,
    banner, ending and credits box shows its id. Still Japanese: only the battle status party name (クルト, phase 8,
    known). The `KLT` tile on the HP box portrait and the `YES/NO` icons are the original's own graphics; stray
    `よらw` tiles at the right edge of `svc_0B_00`/`svc_0D_00` are leftover BG3 map from the room scroll, not text.
    **Item name fields per list** (`asm/vwf.asm`: hook `nm_f3c3` at 01:F3C3 + table `nm_icap`, also the cap in
    `nm_feaa`; `docs/re/windows.md`): each list drawn by 01:F3C0 gets its own width: 9 tiles in the shop buy list
    (the price follows the name; 12 pushed it out of the window) and in FA11/FA16/FA09/FA4B (which hand the space
    before the name to it), 8 in the field item window FA0E (no spare tile). Test
    `test_item_name_fields_fit_their_windows` checks every window script row against its header width. Shots:
    `work/qa/cap` (item window, shop), `work/qa/cap2` (shop at 12).
  - **Phase 5, session 2026-11-24 (10):** consolidated battle tour `work/qa/bcov_all` (all 23 routes, `--jobs 3`,
    5200 frames): 39/133 (40 with the earlier runs; the 94 unread are the state-gated families below). Width gate
    rows added to `docs/re/windows.md`: epilogue = 216 px (40-digit ruler, `work/qa/epi`), shop/inn/healer talk and
    item-use messages = the 216 px dialogue box, field item list = 2 columns of 11 tiles, BG3 menu strings = JP tile
    count, battle rects = `w` x `h` tiles. Item-use flow reachable by poking items (`menu_item` keys + 4 more A,
    `@19CF:4342,@19D1:4544`, `work/qa/mitem`). Synthesis screen: code located (bank 29, `docs/re/battle.md`
    §Coverage) but not reached; magic-healer args 00/01/02 only heal. Full marker re-tour started on the current
    marker build: `work/qa/marker_tour2` (see Next 1b).
  - **Phase 5, session 2026-11-24 (9):** battle tour 20 -> 40/133 ids read (union of `work/qa/bcov2..9`): orders
    sub-commands まほう/ねらう/アイテム/そうび (left/right before A picks one), たれを？, item descriptions (11),
    "no weapon to equip", equip stat box `18640A`, use messages `18653A`/`186562`, victory `140017`. Inventory by
    poke: item ids at record +$CF (`docs/re/debug.md`); 9 routes added to `battle_routes.tsv`; `battle_cover.py`
    takes an optional 7th column (ops hex, no `ops:` prefix). The field scene tour with `rect_reads.lua`
    (`work/qa/rcov_scenes`, 114/114 reached) reads no battle rect beyond the battle scenes: `battle.json` is
    battle-only plus the magic-healer synthesis screen. Spell info column source traced (not a ROM rect: WRAM
    tiles, phase 8; `docs/re/battle.md` §Coverage) with new `tools/lua/bank_reads.lua`. A consolidated
    `battle_cover.py work/qa/bcov_all` run was stopped by the host for low memory; re-run it first.
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
  0. **Phase 8: QA in the emulator** (done-when in the skill table: smoke, tour sheets with visual-QA verdicts via
     `qa_gate.py`, graphics text English, `inkbox.py` on choice/centred boxes, stress saves, `textcover.py` 0).
     Phase-8 items from phase 7: the 8 ids in `script/keep_jp.txt` (battle particles and `bt_19D4BB`: see them in a
     battle, then translate or blank; enemy_40/69: shoot the encounter, `@1DDF`); find the screen of the equip labels
     `bg3_A729/A737/A73D` (Wpn/Shld/Feet, 4 tiles assumed) and the teleport list at 9 letters (`MENU_CAP`); the
     Japanese ま in the status screen's bottom-right window (`work/qa/p7/menu_status/final.png`). Minors in
     `docs/polish.md`; worth a `codex exec -s read-only` story pass once its quota is back (2026-11-26).
  1. **Carried from phase 5** (not blocking translation; the battle part belongs to the phase-8 coverage pass):
     - **1a. Battle-window marker tour** (`battle_cover.py`, 40/133 read; consolidated run `work/qa/bcov_all` done,
       use `--jobs 3`). Still unread and why: `19E09C-19FABE` + `16EF84+` = magic synthesis screen (bank-29 code
       29:D4xx-E8xx, not run by the healer scripts E4 06 00/01/02, E4 07 01: find its entry, `docs/re/battle.md`
       §Coverage; if it stays unreachable, force-call the scripts from a Lua hook in a battle state to see the markers);
       `198926/36/46` other members' names (needs a 4-member party: `$3E`/`$0600` pokes at READY did not do it;
       find what the battle unit setup 29:B216 reads, or use a story save); `1D82xx` status effects, `1865xx`/
       `1866xx` use messages, `1991BB`/`1992DB` no spells / not enough MP, `19F1F3/19F247/19F39F` yes/no
       confirms, `19D4BB` (クルトに...). If whole families never fire a CPU read, check for DMA from ROM.
       Old notes: with pokes
       `god,@1DDF:0053` from room 0x00 40 30, READY is f2149 and the gray command menu is up at ~f3390, so keys
       start with `1100 -` (`tools/debug/probe.py work/qa/bcmd --rom build/marker.sfc --frames 4400 "0x00 40 30 1100
       -;6 right;30 -;6 a;60 -;6 a;200 -|-|god,@1DDF:0053"`). The battle
       auto-fights first: menus need the right moment. Confirm or fix the 12 `scan` geometries (one row, guessed):
       find the reader of `0x140017` (victory), `0x16EF84+` (mana screen, bank $2D), `0x19895C+` with
       `snes_romreads.lua`. Rank form of the spell-cast window still unseen. The 8-byte table at `0x182C57`
       (クルト, メイ, ボルグ, レジーナ) had no reader in `battle_field`; find its user. Enemy names `enemy_40` /
       `enemy_69` use two-row kanji bytes: shoot them in battle for the translator (`@1DDF` picks the encounter).
     - **1b. Full marker tour: done** (session 11, see Done). Re-run it after the battle work if any new text kind
       gets extracted.
     - **Item lists, left:** find the screens behind FA11/FA16/FA09/FA4B and shoot each with 9-letter names. The
       callers of 01:F3C0 over 22 menu/shop scenes (`work/qa/icap`, `run_scenes.py build/marker.sfc --script
       tools/lua/stack_log.lua --var "ADDRS='01F3C0'" --var DEPTH=4`) were only `F2EB` (FA3C shop): the scene
       saves hold no items, so re-run with the item pokes `@19CF:4342,@19D1:4544` (give/trade, equip, sell, item
       use target) to reach the other lists. Japanese byte names (not
       escapes) in a list that gives its space to the name would draw one tile left; only the identity build has
       them.
     - Name entry opens with rows `56789` / `: +` above the cursor row `ABCDE` (the view shows 2 rows before row 0,
       as the kana grid did): consider reordering `insert.NE_GRID` so the first view starts on letters.
     - **BG3 caps for FA inserts**: names inserted into BG3 strings (FA0F/FA18/FA2B/FA2F/FA42) all reach 01:FEAA
       through the same handlers (FA2F -> FA8A -> FE09, return FE1E/FA8F), so a return-address cap table can't tell
       screens apart there; key on the FA op instead (VM pointer `$10` - 2) or let translators lay out rows for an
       8-tile name. Shop list (FE76 <- F3C2) and character names (FE55 <- EF07) can use the return-address table.
     - **BG3 name fields** (01:FEAA path; `docs/re/vwf.md` §Names): item record names done per list (above).
       Character names (01:FE3B, `LDA #$0008`) still 8. Probes for the item window and the shop with poked items:
       `tools/debug/probe.py work/qa/cap --rom build/cap.sfc --frames 3000 "0x4D 10 6 60 -;6 a;40 -;6 right;40 -;6
       right;40 -;6 right;40 -;6 a;90 -;6 a;120 -|-|@19CF:4342,@19D1:4544" "0x4D 10 6 30 -;6 a;60 -;6 a;60 -;6
       a;60 -;6 a;90 -;6 a;90 -;6 a;90 -;6 a;120 -|00E400|@19CF:4342,@19D1:4544"` (build `build/cap.sfc` with
       `build.py --out build/cap.sfc --qa item_42=Abcdefghijkl ...`).
     - **Description boxes** (item/spell descriptions in the shop and spell screens, now `bg3_A3xx`-`bg3_ACxx` in
       `menus.json`): 5 tiles per line x 4 lines of 8 px fixed tiles, far too small for English. Plan engine work
       (wider box via the window op, or draw them through the VWF canvas) and measure the result.
     - Width gate still to measure (`docs/re/windows.md` "Still to measure"): the item-description box
       (`common`/bank-04 descriptions, `menu_item` > item > info), BG3 name fields per screen (`stack_log.lua --var "ADDRS='01FEAA'"` over the menu, shop
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
- **Waiting on the user:** non-blocking: item names are 9 letters (D18; a few abbreviated, listed in
  `docs/polish.md`): say if you want the bigger engine change (one-column item lists, new cursor logic) for full
  12-letter names. Non-blocking: item/spell description boxes are 6 x 7 and 7 x 4 fixed 8 px tiles; the
  default (D9) writes terse English to them; say if you want the engine change that draws descriptions through the
  dialogue VWF in a wide bottom box instead. Non-blocking: BG3 list names (shop list etc.) use a fixed 8 px font with lowercase rather
  than a VWF, since BG3 has no free tiles for one; default kept, say if you want the bigger engine change.
