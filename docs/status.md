# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9, released. Owner asked to publish (D20, v1.0; D21 keeps the save fixture in history). Build
  d8905718: tour9 (120/120) copied into tour2, gate re-inited on it, 272/272 ok (34 carried from tour8, 238 from 8
  reviewers, `work/qa/verdicts/`). `tools/release.py --version 1.0 --force` passed: `release/LastBattle_EN_v1.0.zip`
  (patched CRC32 9360A5FC, SHA-1 53d516ea; bps SHA-1 3fa818b1). Published as GitHub release v1.0, repo public.
  2026-11-24 session 35.
- **Next:** (1) player bug reports (`gh issue list --label bug`); (2) the svc_cover runs `review bmagic bparty
  bparty2` on the new build, one at a time (`--jobs 1`: two runs were stopped for low memory), looking for
  full-canvas fallbacks (a run left in fixed cells) and garbage tiles; (3) owner's call: VWF for the battle lists
  too (item/spell names come from WRAM rects, still fixed cells; needs the second canvas range `$1FD-$27F`).
- **Done:**
  - **Phase 9, session 2026-11-24 (35):** visual gate on build 55bf5596 (tour8, 8 reviewers, round now in
    `work/qa/s34_round`) found 10 problems, fixed or waived (`docs/polish.md`, session 35 lines): item descriptions
    5 tiles per line and 4 on the last (shop panel; `extract.DESC_BOXES`/`DESC_LAST_SHORT`, lint, test; 27
    rewritten), dakuten rows above Borg/Regina cleared, typed battle messages centred with blank pad glyphs
    (`bvwf.PADS`, `battle_text.column_rows`), LEVEL UP!! one run and centred, r320/r319 one-word lines, "Quit"/"Cast"
    labels padded, equipment "E" marker under 9-tile names waived (D18). Lint reads `{F9FF}` as a page break.
    `battle_items` route waits 1400 frames (an enemy turn ate the first A; it showed Cast, not Item). Tour9 restarted
    after a memory kill: batches of 12-30 scenes, `--jobs 1`, about 15 s a scene.
  - **Phase 9, session 2026-11-24 (34):** owner's playtest shots (D19). **Bold BG3 lowercase**: `tools/font_bg3.py`
    glyphs redrawn with 2 px stems like the capitals ("OK"/"No", "Yes", "FILE1" now match). **Battle VWF**:
    `tools/bvwf.py` + asm `bvwf_rect` (hooks 29:A278, 30:F242, 3C:8057, 30:AE2E; canvas BG3 $11A-$17F, shadow
    `$7F:D800`, uploads through the NMI queue 2A:989A; `docs/re/battle.md` §Battle VWF); typed messages copy the
    whole prefix per op (`battle_text.column_messages`). Seen in game: victory line, EX/LEVEL UP windows, item
    descriptions, Kurt can't escape!, Agility up!, Magic power is fading..., No weapon equipped, See an opening,
    tactic menu, All have fallen... (typed), synthesis Combine screens (`work/qa/bvwf4`, `bvwf5`, `bvwf_cover`,
    `bvwf_svc/synth`). New test `test_battle_vwf` (asm constants, canvas range, no run wider than its cells).
    The "What ?" gap in the Cast prompt is the original's two windows (same in v1.0).
  - **Phase 9, session 2026-11-24 (33):** **story pass finished**: ch2-ch6 read in full by the worker (codex out of
    quota), all `ok` (reports `work/qa/story/reports/`). One Minor fixed: r264_064A Duken "I could squash you in a
    second!" (was "crush you in a twist", ticked in `docs/polish.md`; r264 is in no tour scene, so nothing to
    re-shoot). Rebuilt, re-ran `tools/story_chapters.py` and the story `init` (ch6 re-verdicted after its change).
    **Visual gate closed**: the 112 open sheets judged from the `work/qa/novel6` old|new crops (all frame timing:
    fades, typing, sprite and battle-RNG steps; text checks: menu_search "There is nothing there." fits,
    stress_itemuse "Use whose item?" centred at 3x zoom). Ending + credits judged from new
    `work/qa/novel7` (tour7 vs tour6/5/3); the r320 caption reads right. Verdicts in
    `work/qa/verdicts/s33_a.tsv`, `s33_b.tsv`. Visual manifest re-init on the new build (0 sheets changed).
    `tools/release.py --version 1.0 --force` exits 0: tests, smoke, jp_left 0, both gates, textcover, checksum
    09C3, BPS made and re-applied to the clean original (CRC match). Nothing published.
  - **Phase 9, session 2026-11-24 (32):** story pass **ch1_eldar ok, ch7_last_battle ok** (reports
    `work/qa/story/reports/`, verdicts `work/qa/story/verdicts/`), read in full by the worker itself (codex still
    out of quota). ch7 Minors fixed in `script/` and ticked in `docs/polish.md`: r293 Iskar "Heh heh...", Regina
    "casts aside Silvel", r320_0368 ending caption now the r009 wording. ch2 read to line 220 of 869 with nothing found
    (not a verdict). Build **aa13885f**, check.py 0 problems. Re-shot `ending` + `credits` into `work/qa/tour7` (the
    new caption is at `tour7/ending/f014160.png`, reads right), copied into tour2, `qa_gate.py init --build` again.
    Timing check on the 87 tour6 sheets: **88 of 120 final frames are pixel-identical** to tour5/tour3, the other 32
    differ only by cursor blink, sprite animation or palette fade, apart from the intended "There is nothing there."
    (menu_search). New tool **`tools/debug/tour_novel.py`**: for each re-shot scene, crops (old | new) of every frame
    region no earlier tour showed, to `work/qa/novel6/<scene>.png` (+ `summary.tsv`); those crops are what the
    verdicts need reading, not the whole sheets.
  - **Phase 9, session 2026-11-24 (31):** **polish pass**: every `docs/polish.md` line ticked (fixed: the M1
    duplicate-JP lines now share one wording, r009 copies the r319-r322 ending text; "It is locked." / "There is
    nothing there." everywhere; Ritten/Gulva old men's "eh" tags cut by about half; `common_0384` "Zzz... zzz....";
    library caption past tense; shopkeeper "yessir!"; waived with reasons: battle rects too narrow, D9/D10/D18
    limits, cosmetic layout). **`tools/release.py`** (build, tests, smoke, `jp_left.py --known docs/jp_known.txt`
    (12 runs, all code/data/compressed bytes), `qa_gate.py check` on every `work/qa/**/manifest.tsv`, textcover on
    the frozen `work/qa/cover_build/strings.tsv`, polish, README placeholders + base SHA-1, checksum, BPS make +
    re-apply compare, zip `release/LastBattle_EN_vX.Y.zip` = .bps + README.txt from `docs/release-readme.txt`).
    README.md filled (status table, base ROM hashes). **Story pass set up:** `tools/story_chapters.py` writes the 7
    chapter files (synopsis room ranges) to `work/qa/story/chapters/`, manifest `work/qa/story/manifest.tsv`
    (init done, 0/7 verdicts).
  - **Phase 8 done, session 2026-11-24 (30):** `textcover.py` exits 0: **3134/3143 shown, 9 waived, 0 failing**.
    The last three battle messages are RNG/status gated, so two new Lua hooks force the branch (used with
    `svc_cover.py bparty2` specs through a scratch runner): `tools/debug/bfade.lua` clears carry at 29:89CD (the
    Seal Stone fade roll, JSL 2A:9D70 vs $55/$40) -> `bt_186512` "Magic faded away" (`work/qa/cover/fade1`, spec 30);
    `tools/debug/bherb.lua --var BST=1|4` sets A at 29:9270 (Cure Herb target status) -> `bt_1865EA` Poison cured /
    `bt_186626` Confusion cleared (`work/qa/cover/herb1`, `herb4`, spec 21). Build still 5d09a64b: `qa_gate.py check
    work/qa/manifest.tsv work/qa/verdicts` 266/266 ok, smoke ok, check.py 0 problems. Inkbox, graphics text and
    stress saves were done in sessions 22-27 (below).
  - **Phase 8, session 2026-11-24 (29):** coverage 3108 -> **3131/3143 shown, 9 waived, 3 failing**. bparty specs
    7-33 finished (`work/qa/cover/bparty3`: Agility/Defense up, all status effects `bt_1D82xx`, use messages).
    New probe kind `svc_cover.py bparty2` (38 specs, runs `bparty4`-`bparty10`; the system killed two runs for low
    memory, so run it with `--jobs 1` and a few specs at a time). Found and shown: the battle item description
    table `$30:DD73` (0x185D73) is indexed by (item record +$0B & $3F) - 1 (Erase Wand $8B -> "Nulls all magic",
    Pendant $C7/$99 -> "Party defense up"); LEVEL UP rows for Mei/Borg/Regina (win with every member at level 1,
    EX 0: record +$22/+$23); escape 29:86A5 compares the party level `$12A5` with the top enemy level + a roll, so
    Run at level 99 (record +$22 = $63) shows "Kurt ran away" / "Kurt's party ran away"; Gear with two swords
    carried (`@19CF:CECC`) shows the Atk/Def window `bt_18640A`; Erase Wand vs Iskar (enemy $3A, 29:91F5) shows "No
    effect on Ice Dragon!" (Iskar is the JP's Ice Dragon; the non-Iskar branch is "Magic power is fading...");
    a Seal Stone holding Restore with power byte +$0D bit 7 (30:8043) shows the spell info "Party" cell. Waived
    `bt_1F0DD6` "only one tactic" (record `$28:9613` is never loaded, see `docs/text_unshown.tsv`).
    `tools/debug/bstatus.lua` holds a battle status in unit 0 +1 (`$1299`) from a record poke `@1901=0s`.
    **Visual gate passes on build 5d09a64b** (266 sheets): re-shot
    battle_field/room/win, wipeout and the new `battle_items` into `work/qa/tour5`, copied to tour2, `qa_gate.py
    init`, verdicts `work/qa/verdicts/s29_battle.tsv` (item list reads All / Elixir, Blood- / lure, Speed / Herb,
    Erase / Wand). JP `battle_items` shot in `work/qa/tour_jp` (its battle runs on different timing: no item list).
    Smoke ok.
  - **Phase 8, session 2026-11-24 (28):** coverage 3094 -> **3108/3143 shown, 8 waived, 27 failing**. Party battle
    key paths found (`docs/re/debug.md` §Battle: a key during the COMMAND banner opens Atk / Cmd / Plan / Run; Cmd >
    Cast / Item / Gear); `svc_cover.py bparty` rewritten (34 specs). **Bug fixed:** the battle item list cut 9-letter
    names at 8 ("AllElixi/r", "Bloodlur/e", "EraseWan/d"): `insert.battle_rows` now splits inside the word after a
    "." or before an inner capital ("All/Elixir", "Sil./Sword") or at `insert.BT_HYPHEN` ("Long-/sword",
    "Blood-/lure"); the lint checks items/tactics/enemies (`battle_fits`), test in `test_battle_rows`; shot on build
    5d09a64b (the list reads All / Elixir, Blood- / lure, Speed / Herb, Erase / Wand). New scene `battle_items`
    (not yet in the tour). Enemies: Iskar is group `$8888`, Sky Walker shows in the title attract demo
    (`work/qa/cover/attract`, 20000 idle frames); the other 8 are waived in `docs/text_unshown.tsv` (only three
    loaders fill `$1715/$1717`, none has them; 5 are placeholder records). Disk was full (0 B): per-frame PNGs in
    `work/qa/cover_v1` deleted (20 GB free after). The bparty run was **killed by the system for low memory** after
    specs 0-6.
  - **Phase 8, session 2026-11-24 (27):** coverage 2512 -> 3094/3143 shown (49 left: 39 `bt`, 10 `enemy`). Session 26's three runs had died
    (no DONE lines): redone. All room strings, all `b04`, all `bg3` now shown. **Bugs fixed:** (1) item > Examine
    printed "Gladius / 武器 / 攻撃力 / 8 UP": three bank-04 pointer tables were never extracted (`0x247D9` FA3E
    categories, `0x24805` FA3F stats, `0x24831` FA40 UP/DOWN; `extract.B04_TABLES`, ranges `232D2-24844`, b069:
    Weapon/Armor/Shield/Footwear/Accessory, Attack/Defense/Agility/Wisdom/Luck, up/down); shot "Gladius / Weapon /
    Attack / 8 up" (`work/qa/exam_cat`). These 12 ids are not in the frozen coverage set: covered on build c98763d5
    (`work/qa/exam_cat2`, `exam_cat_rom.sfc` + `exam_cat_strings.tsv`): 11/12, DOWN waived (unreachable, see
    `docs/text_unshown.tsv`). (2) The magic synthesis screen (healer E4 07 00 > Combine/Review/Split, first reached
    this session) showed `High "Bal"ance` (dakuten row 0x40 above a bank-$2D scan row: `battle_text.dakuten_above`
    blanks it) and "FWind"/"WaFire" in the mana boxes (template rows `bt_16EF84`/`bt_16F082` now aligned like the JP,
    mana names `bt_19E09C-E4` in the bottom row only; b070, b071). Shot on the current build: `work/qa/synth_en`
    vs `work/qa/synth_jp`. New probe tool `tools/debug/svc_cover.py` (chest, magic, seal, synth, review, bmagic,
    erased) and `load_fail.lua`; `names_cover.py --ids`, `owmenus`. `{num}` digits in dialogue are the old tall
    font (polish.md b04_C763). (3) Battle Cmd > Cast prompt showed `"ho?` under a stray W: だれが？/だれを？ are 4x2
    rects (dakuten row first), not the guessed one-row scans (`battle_text.EXTRA_RECTS`, ids now `bt_198956` /
    `bt_198986`, `extract.RENAMED`), both "{nl}Who?". The battle spell list/info column ("Spell Seal / All / Rate")
    reads fine; "What ?" with a gap is the JP's own leftover ？. Battle party = `$1DD4-$1DD7` (found).
  - **Phase 8, session 2026-11-24 (26):** session-25 re-run finished (`cover_rooms3.log` "RERUN DONE", 119/119
    scenes). With the decompression reads gone the true gap showed: ~900 room strings sit in branches behind story
    flags that no room run takes. New probes: `tools/debug/strings_cover.py` runs the VM straight at each unshown
    room string (text is inline in the VM stream: textcover_run.run_room with the string offsets as entries; room 2
    test: 16/16 shown) and, with `--top`, the shop/inn/healer and common-block strings via `tools/debug/topstr.lua`
    (op E4 lo / E5 00 in room 0x4D; when the block's stream is decompressed (00:83A7 entry, exit 00:8410) every used
    slot of its word table is pointed at the string): **all 126 top/common strings shown**. `names_cover.py battles`
    (one idle god-mode battle per group id 0x00-0xBF for enemy names), `names_cover.py menus` (field-menu walks with
    a 4-member party: poking `$3E` = 4 and `$0600` = 0,1,2,3 at READY works in the field), `tools/debug/cover_battle.sh`
    (the session-24 battle probes, redone). Re-shot the 44 scenes changed in session 24 (`place_*`, menus,
    `stress_itemlist`) into tour3 and copied their sheets to `work/qa/tour2` (the manifest's dir: never pass tour3
    as a second init dir, it duplicates every id as `../tour3/...`); 30 changed sheets got verdicts
    (`verdicts/chunk_fbbaff1ab064.tsv`, banners inkbox-centred within 3 px); **gate passes on build ac401138**.
  - **Phase 8, session 2026-11-24 (25):** scene coverage pass finished (`place_22`+, all `svc_*`). New probes in
    `tools/debug/names_cover.py`: `spells` (Kurt's 12 spell slots are `$1927 + 14i`, flag byte bit 7 = known; all 28
    spell names drawn), `itemdesc` (cursor walked over 16 poked items: the description box left of the item list),
    `spelldesc` (22 spell types: low 5 bits of the slot's flag byte), `sealdesc` (seal items `$F5-$FF`, sealed spell
    slot at `$1CF1 + 14k`: the 23 short spell names), `examine` (item > Examine long descriptions, 2 items a run),
    `use` (field item use on Kurt, HP/MP poked to 1). Report went 718 -> 600 unshown before the probe fix below.
    **textcover.lua bugs fixed** (`docs/re/debug.md` §Text coverage): the decompressor reads its arguments with
    absolute `$00AC-$00B2`, so the common block (E5, called with D = `$0C00`) was never keyed (all 33 `common_*`
    unlogged although rooms call them); and the LZ decoder's copy reads of `$7F` (`00:8621`) logged block strings at
    decompression time (e.g. `r009_00D8` "shown" a frame after `BLOCK`). Every block-key log before this session is
    unreliable: old room/scene/variant logs moved to `work/qa/cover_v1/`, full re-run started with
    `tools/debug/cover_all.sh` (logs `work/qa/cover_rooms3.log`, `cover_scenes3.log`; "RERUN DONE" at the end).
    The session-24 `battle` and `wipeout` probe dirs were moved too and are not in `cover_all.sh`: redo them (their
    commands are in `work/qa/cover_v1/{battle,wipeout}*/_run.lua`). `examine` closed ~50 b04 item descriptions
    (report 550 while the old logs were still counted).
  - **Phase 8, session 2026-11-24 (24):** text coverage re-run at 3-4 emulators: all 323 rooms + 14 variants done
    (`work/qa/cover_rooms2.log`; `textcover_run.py --skip-done` skips rooms an earlier run finished), menu/scene pass
    (`work/qa/cover/scenes`), item lists with every unseen item id poked into Kurt's 16 slots (`work/qa/cover/names`
    p00-p03: all 135 item names now shown). **Coverage set is frozen to build 84d80ad0**: `work/qa/cover_build/rom.sfc`
    + its `strings.tsv` (spell keys fixed, see below); later builds shift every block key by a byte, so run all
    further coverage probes with `--rom work/qa/cover_build/rom.sfc` and report against that `strings.tsv`.
    `strings_tsv.py`: spell names are read from the character records in WRAM, never from the ROM slot, so their
    key is now the English name in NAMES_AREA (`$FC:8000` table, kind 2). inkbox pass (tol: BG3 text is 8 px tiles,
    so the best centring is +-8 px; VWF banners +-4 px): 33 place banners were 2-4 px left (pad now rounds to nearest,
    `batches.wrap`, fix batch b068, 19 changed); "What now?" (bg3_8600) and "Use which item?" (bg3_86D2) moved a tile
    right, bg3_867A reworded "Use whose item?" to centre in its 21-tile slot; prompt bars, Yes/Save/Cast/Ster/Pick
    Plan label boxes and the item-menu message bar all within a tile (script: scratch, rects `21,59,214,16` prompt
    bar, label boxes found by their white borders at y 119-141, banners `53,180,150,22` / top `53,28,150,22`, all
    `--ink 239,239,239 --diff 20`). Graphics text: none left in Japanese (title/logo English already, no chapter-card
    or game-over graphics; spell info labels seen in session 23).
  - **Phase 8, session 2026-11-24 (23), part 2:** QA gate passes on tour3 (43 scenes re-shot after a full disk).
    Text coverage: `build.py` writes `build/strings.tsv` (`tools/strings_tsv.py`, block strings keyed by stream),
    `tools/debug/textcover.lua` (block-aware probe + script chaining), `tools/debug/textcover_run.py` (every room
    and the 14 story-variant blocks), warp.lua ad-hoc `RUN`; test in `test_english_build_moves`. Partial run only.
  - **Phase 8, session 2026-11-24 (23):** full visual pass of the re-tour (`work/qa/tour2`, then `tour3` on the
    fixed build; page-end extraction for the long scenes, inkbox on the prompt bar). Fixed: (1) party wipeout
    "全滅しました・・・" was garbled kana columns: `battle_text.column_messages` now walks any column script to its FF
    (column from the op's VRAM dest) -> "All have / fallen..."; column data moved to `$FE:8000` (0x3F0000, the
    `$2A:8FF0` spare was too small); `bt_19D4BB` グルド軍に遭遇! = "Guld's / army!" (29:8256, unseen: needs
    `$180A`=0x14). (2) Battle item drop "Mana / Herbを y.dれu": 30:ADF8 stored を_てにいれた as immediates ->
    `battle_text.found_message` stores "found!". (3) 32 field prompts sat up to 2.5 tiles left of the JP centre
    (`batches.wrap` capped them at the JP string's tile count): cap now the 26-tile prompt box (`MSG_BOX`), half
    rounds up, JP trailing blanks ignored, `{009F}` counts (b067; inkbox save_confirm 36/79 -> 60/55). (4) The
    item-name label beside the menu icons (FA18 windows `0x21656`/`0x21660`) widened 8 -> 9 tiles: "Longsword" was
    under its border. Seen OK: battle spell info Flame / 1 foe / Pow / Rng / MP (field magic), Basic tactic box,
    Fireball / A cast box, all 33 place banners, all shops/inns/healers, stress saves, epilogue. Minors to polish.md.
  - **Phase 8, session 2026-11-24 (22):** visual review of the tour found battle bugs, all fixed and shot:
    (1) `tools/blz.py` encoder emitted self-overlapping copies the game's decoder (30:F5C1) reads as old window bytes:
    every battle had garbage tiles (lines in all box borders, `!` as a cross); decoder now models it, encoder keeps
    length <= offset, VRAM dump matches (`docs/re/battle.md`). (2) "敵の奇襲攻撃!!"/"奇襲攻撃に成功!" (typed column by
    column from shared kanji columns) -> "Enemy/ambush!!", "Surprise/attack!" (`battle_text.column_messages`,
    columns at `$2A:8FF0`). (3) Victory line: suffix now after the name's last non-space (asm 3C:8041), "Purple /
    Slimes defeated!". (4) Battle text scan widened to banks $28-$3F (`re_battle_text.BANKS`, `EXTRA_RECTS`): 57
    bank-$3E rects (EX / mana / LEVEL UP windows with Kurt/Mei/Borg/Regina and Atk/Def/Agi/Wis, escape messages from
    the 7-byte records at 0x1415B6, the battle magic window's spell info column) translated in b063-b065. Shots:
    `work/qa/vic4` (victory + level up), `work/qa/run` (Kurt can't / escape!). Not yet seen: the mana window header
    `bt_1F0198` ("Fire Wind Wat Ea", positions guessed), "Surprise attack!", the battle spell info column.
    `tools/debug/review_sheets.py CHUNK` makes 1x review pages per scene (`work/qa/review/<scene>/r*.png`).
  - **Phase 8, session 2026-11-24 (21):** JP reference tour `work/qa/tour_jp` done (119 scenes). Battle status-box
    party names English (`font_bg3.battle_names_patch`): second battle LZ stream redrawn in a compact 4 px font,
    re-encoded right after the battle font (both load lists repointed), Borg on 2 new tiles $1FB-$1FC (zero and
    unused in battle VRAM) since ボルグ shared Kurt's kana; tilemap rows raw at `0x1F084A` (+0x1E per member). Shot
    Kurt/Regina/Borg via scratch variants that point Kurt's row at the other tiles (`work/qa/names_*`). enemy_40/69
    read from the battle-font kanji: 鬼人 "Oni", 戦人機 "War Machine" (glossary). The status-screen ま is gone
    (`↓Mag`, session 20). Battle command label reads "Atk" (no longer garbled). Codex quota is out until
    2026-11-26, so verdicts are written by the worker itself.
  - **Phase 8, session 2026-11-24 (20), started:** status screen bottom-right `↓まほう` was `↓まMg`: the extractor's
    byte-at-a-time resync swallowed a window header and the first tile; `extract.bg3_strings` now skips a 4-byte
    header after FF00 (only change ROM-wide: `bg3_915C` -> `bg3_9158` "{00A1}Mag"). Status "Fenamun" label one
    column left (it touched its dot field). Stress save `stress_items.srm` (16 slots of 9-letter items, file name
    WWWWWWWW, money 9,999,999; character names are fixed ROM strings, `$0024` is only the file name) and scenes
    `stress_load/status/itemlist/itemuse/equip`: all read ok (`work/qa/stress`). `docs/visual-qa-brief.md` with
    the game's standing non-bugs. Full tour `work/qa/tour` on build sha1 8b50fe77: 119/119 scenes reached. Use `--jobs 3` for tours (5 jobs plus the session ran
    the machine out of memory).
  - **Phase 7 review, session 2026-11-24 (20):** `.harness/reviews/last-battle-the-en-phase7.md` I1: FA18 item
    names in BG3 messages now print 9 (asm `nm_feaa`, return $FC70; FC55 is reached only from the op table), shot
    "Gave Kurt Longsword." / "Equipped Longsword." / "Dropped Rare Herb." (`work/qa/i1e`, `work/qa/i1d`). M1: lint
    counts name inserts at their longest (`batches.INSERT_TILES`, prompt box 26 tiles measured, `MSG_BOX`); it
    found 2 lines over at worst-case names, fixed in b062 ("Gave {FA42} {FA18}.", "No {FA18} for {FA0F}."). M2:
    D18 reworded (headers keep the full form where the list name is a squeeze). M3: `BankPools.repoint` asserts
    each slot's original pointer. M5: `docs/re/battle.md` note. M4 stays on the phase-8 list. Next free fix: b063.
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
  000. **Session 33 hand-back: release ready, the user publishes.** `release/LastBattle_EN_v1.0.zip` is built and
     verified (see the Phase line). Publishing (`gh release create`, repo visibility) is the user's call; never do it
     unasked. If text changes before then: fix in `script/`, rebuild, re-shoot only the scenes showing it, copy into
     tour2, `qa_gate.py init work/qa/manifest.tsv work/qa/tour2 --build build/lastbattle_en.sfc`, judge the new
     crops with `tour_novel.py`, re-run `tools/story_chapters.py` + story `init` (a changed chapter needs a new
     verdict), then `tools/release.py --version 1.0 --force`.
  00. **Phase 9: Release (session 31 notes).** (1) **Story pass**, 7 chapters: `qa_gate.py todo work/qa/story/manifest.tsv
     work/qa/story/verdicts --size 1`. For each chapter, a fresh read-only reviewer (brief
     `$SKILL/assets/story-reviewer-brief.md` with this game's names; inputs `docs/synopsis.md`,
     `docs/style-reference.md`, `glossary.md`) reads the whole file in parts (Read with offset/limit, 60-75 rows:
     the files are 41-208 KB, ch4 is the largest) and returns Issues + Assessment. `codex exec -s read-only` is out
     of quota until 2026-11-26 10:32; without it, do one or two chapters per fresh worker context yourself. Save
     reports to `work/qa/story/reports/<ch>.md`, write `<ch><TAB>ok|issue<TAB>note` to
     `work/qa/story/verdicts/<ch>.tsv`, fix every Critical/Important in `script/` (then rebuild, re-run
     `tools/story_chapters.py` and `qa_gate.py init` again: a changed chapter needs a new verdict), Minors to
     `docs/polish.md` (tick them before release). (2) **Visual gate is open on build 8934b957:** session 31 re-shot
     all 120 scenes into `work/qa/tour6` (120/120 reached), copied each `sheet.png`/`final.png` into `work/qa/tour2`
     and ran `qa_gate.py init work/qa/manifest.tsv work/qa/tour2 --build build/lastbattle_en.sfc`: **87 of 266
     sheets changed** and need verdicts (`qa_gate.py todo work/qa/manifest.tsv work/qa/verdicts --size 30` lists
     them: battle_*, camp_menu, credits, ending, menus, name entry, saves, stress_*...). Most are probably frame
     timing, not text (the session-31 edits touch only dialogue, the ending text r009 and two field messages):
     check with `sheet.py --compare` against `work/qa/tour5`/`tour4`/`tour3` first, then write verdicts chunk by chunk
     (`docs/visual-qa-brief.md`) to `work/qa/verdicts/s31_<chunk>.tsv`. If text changes again later, re-shoot only
     the scenes showing it and re-init. (3) `python -X utf8
     tools/release.py --version 1.0` must exit 0 (it checks everything else). Never run `gh release create`.
     Phase-8 leftovers judged non-blocking: equip-label screen `bg3_A729/A737/A73D`, teleport list at 9 letters,
     name-entry grid order. The phase-8 notes below are history.
  0. **Phase 8: QA in the emulator** (DONE session 30; done-when in the skill table: smoke, tour sheets with visual-QA verdicts via
     `qa_gate.py`, graphics text English, `inkbox.py` on choice/centred boxes, stress saves, `textcover.py` 0).
     **Resume here (session 29 end):** 3 failing, all battle messages. Run probes with `--jobs 1`, a few specs a
     run (memory). (1) `bt_186512` "Magic faded away": 29:8992 handles a used item id >= $F5; at 29:89B4 a Seal
     Stone fades on a roll < $55/256, a Seal Tome on < $40 (then the slot is cleared). Specs 30-35 (stone with
     Restore / Fireball) ran 4 times with no fade: check in one run's frames that the stone was really used (maybe
     30:8043/30:806E send it to 29:8AFE first), then run specs 32-35 or add more timings. (2) `bt_1865EA` Poison
     cured / `bt_186626` Confusion cleared: Cure Herb (effect $0C) -> item jump table 29:9176 -> 29:924E -> 29:9259:
     status = battle unit +1 & 7 (`$1400` from 30:8F1D = `$1298 + i*$28`; 1 poison -> DE36, 2 stun, 4 confusion ->
     DE48), and a bit in the table at `$00E8` (29:CCEA) also routes to the confusion branch. Specs 21-22 with
     `bstatus.lua` held unit0+1 = 1 / 4 from f2357 on, the herb was queued on Kurt ("OK!"), yet no use message showed
     at all: read the frames after f4290 in `work/qa/cover/bparty9/p00*`, and log unit0+1 and the action with
     `tools/lua/watch_value.lua` (maybe status 1 stops Kurt acting, so let Mei use the herb on Kurt). Or a natural
     route: an enemy that poisons (find its group). Waive only with the reason. (3) Then the report must exit 0.
     Older (pre-session-29) notes follow.
     Session 28 notes: (1) finish the bparty probe, at most 2 jobs because memory ran out:
     `python -X utf8 tools/debug/svc_cover.py work/qa/cover/bparty3 bparty --jobs 2 --only 7,8,...,33` (specs
     0-6 done in `bparty2`), then report. Still failing: battle use messages `bt_18617F-186662`, status effects
     `bt_1D8245-830B`, item descriptions `bt_185F09`/`bt_18612F` (Nulls magic, Party defense: the walk missed them),
     party LEVEL UP rows `bt_1F04E8-0568` (spec 0 won, but no member levelled: poke record +$23 EX near the next
     level, +$22 level), "Kurt ran away"/"party ran away" `bt_1F0D06/0D36` (escape is random: more Run specs),
     `bt_1F0DD6` (only one tactic), `bt_1F0F14` ("{nl}Party"). Waive what stays unreachable, with the reason.
     (2) Build changed (5d09a64b, battle name split): re-shoot battle_field/battle_room/battle_win/wipeout plus the
     new `battle_items` into a new tour dir, copy to tour2, `qa_gate.py init ... --build build/lastbattle_en.sfc`,
     write verdicts for the changed sheets. Older note: visual-QA gate PASSED (263/263) on build eb6d073d (session 27 re-shot battle_field/room/win
     for the Who? fix into tour4, copied to tour2, verdicts `work/qa/verdicts/s27_battle.tsv`; the other scenes
     have no text this session changed). Smoke ok. Text coverage (all probes on `work/qa/cover_build/rom.sfc`,
     everything under `work/qa/cover`): report `python -X utf8 $SKILL/scripts/textcover.py work/qa/cover
     work/qa/cover_build/strings.tsv --waive docs/text_unshown.tsv --mask 0xFFFFFFFFFFFF > work/qa/cover_report.txt`.
     **3094/3143 shown, 1 waived (b04_C83B, not in the set's tsv), 49 failing**; every room/top/common/b04/bg3/menu
     string is shown (group sweep and `cover_battle.sh` done: `cover_battles.log` BATTLES DONE). Left, all battle-only:
     (a) **party battles**: `svc_cover.py bparty` gets all four members into a battle (`$1DD4-$1DD7`, docs/re/debug.md)
     and closed the victory-window names, but its Run and Item key paths were wrong with a party (the command order
     differs: `right;right;a` opened the tactic list). Find the path (shoot a party battle, read the menus), then:
     escape messages `bt_1F0D06-0DD6` ("Kurt's party ran away" etc., also "There is only one tactic"), LEVEL UP rows
     for Mei/Borg/Regina `bt_1F04E8-0568` (win with the party and enough EX: poke their level/EX low), battle item
     descriptions `bt_185DF1-18612F` (cursor over Herb..AllElixir in the battle item list), battle use messages
     `bt_18617F-186662` (No items, No weapon, Magic faded, Agility up, Poison cured...), status effects
     `bt_1D8245-830B` (Wis up / Atk up: cast MagicArm/Haste in battle via `svc_cover.py bmagic`-style keys + A).
     (b) enemy names still unseen after the full group sweep (`names_cover.py battles`, ids 0x00-0xBF): check
     `re_encounters.py` / scripted boss battles (room scripts start fixed battles: find the op) or waive with the
     reason. (c) Everything frozen to cover_build: the 12 new Examine strings (b069) are covered separately on
     build c98763d5 (see Done); bt_198956/198986 replace bt_19895C/198988 (same rect, read in the old set).
     When the battle gaps are closed or waived, rebuild a fresh coverage set on the final build only if a later
     text change shifts streams (see `docs/re/debug.md` §Text coverage).
     Write verdicts chunk by chunk to `work/qa/verdicts/<chunk>.tsv` (brief
     `docs/visual-qa-brief.md`; compare `work/qa/tour_jp/<scene>`). Budget: 261 sheets are 520x456 with 128x112
     tiles, too small to read text, so for each scene zoom the text boxes (`sheet.py DIR --changed 0.03 --crop
     0,150,256,74 --div 1 --cols 3`; battle top boxes `--crop 0,0,256,64`) and read `final.png`; about 3 chunks
     fit in one worker context, so hand back with the verdicts written so far.
     Phase-8 items left: the spell info labels right of the battle magic window
     (いりょく/しゃていきょり/MP, tiles from a WRAM block: graphics); find the screen of the equip labels
     `bg3_A729/A737/A73D` (Wpn/Shld/Feet, 4 tiles assumed) and the teleport list at 9 letters (`MENU_CAP`);
     `inkbox.py` on Yes/No and centred boxes; `textcover.py`. Minors in `docs/polish.md`; worth a `codex exec -s
     read-only` story pass once its quota is back (2026-11-26).
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
- **Waiting on the user:** Non-blocking: item names are 9 letters (D18; a few abbreviated, listed in
  `docs/polish.md`): say if you want the bigger engine change (one-column item lists, new cursor logic) for full
  12-letter names. Non-blocking: item/spell description boxes are 6 x 7 and 7 x 4 fixed 8 px tiles; the
  default (D9) writes terse English to them; say if you want the engine change that draws descriptions through the
  dialogue VWF in a wide bottom box instead. Non-blocking: BG3 list names (shop list etc.) use a fixed 8 px font with lowercase rather
  than a VWF, since BG3 has no free tiles for one; default kept, say if you want the bigger engine change.
