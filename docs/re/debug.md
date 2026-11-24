# Debug tool: RAM map and hooks (phase 2)

Everything `tools/debug/warp.lua` relies on. Addresses are WRAM (`$7E`) unless a bank is given.

## Map change (verified: warps to 80+ rooms from a cold boot, `work/qa/scenes`)
- Request block `$0D22-$0D2B` (DP `$0D00` in the loader): `$0D24` room id (1-based; 0 = overworld), `$0D26` x,
  `$0D28` y (tiles), `$0D2A` facing, `$0D22` mode byte. Script op **BA** writes it (`BA lo, w room, b x, b y, b dir,
  b flag`: also sets story flag `$0200+flag` = 1), sets `$0010` = 0 (next mode), `$CE` = 1 (change pending),
  `$CC` = 2 (fade speed) and calls `00:9648` -> `00:964C` (prepare: clears `$0D4A-$0DFF`, `00:96EA`, then
  `00:B169` / `00:A5B1` for the overworld, which load the room script block via `01:E631`, A = room - 1).
- `00:80DF` (main loop): when `$CE` != 0 and the fade (`$CC`) is done, `00:9679` switches: `$0D24-2A` -> `$2C`
  (current room), `$2E` x, `$30` y, `$32` facing; `$1DDF` = `$FFFF`; then room 0 -> `00:A67B`, else `00:B367`.
- New game (`01:B693`): request room 2, (6, 7), facing 2; party size `$3E` = 1, `$0600` list; music `$0D3A` = `$0E10`.
- **warp.lua** overwrites the request at the first `00:964C` (the new-game load), so the game loads the target room
  itself. Room 0 (overworld, mode 7) takes tile coordinates; (40, 30) is land next to the first village.
- Room entry positions are not in a table found so far (doors are not BA ops; only 70 BAs exist, listed by
  `script_dis.py -v`). `place_*` scenes use (10, 8), which can be inside a wall: the room still draws.

## Scripts on demand
- Entry script: `00:D656` reads `$7F0000` (e0) -> `$0C10/$0C12`, VM call `00:D666`. Replacing it skips the room's
  fade-in (black screen), so warp.lua does not.
- Field loop `00:9786` calls `00:D634` each frame: when `$0634` != 0 it runs the room's e1 script (`$7F0002`). warp.lua
  sets `$0634` = 1 at READY and, at the VM call `00:D64C`, points `$0C10/$0C12` at its own bytes in free WRAM
  (`$7EFF00`, zero in every dump checked) followed by `FF00`. Used for **E4** services: `E4 lo, b arg` loads
  top-table block `14 + lo` (`01:E614`, table `$1A:801E`), runs its script `arg` (`01:D25D` jump table), then reloads
  the room block (`01:D24F`). lo 00/01 shops, 04/05 inns, 06/07 magic healers (heal / synthesise / check /
  decompose magic), others: see `svc_*` scenes.

## Battle
- Field loop `00:979E`: `$1DDF` != `$FFFF` starts a battle with that encounter group (`00:A1F2`; engine in banks
  `$28-$30`). Random encounters: `30:EBD9` walks `$2A:A080` (zone key, pointer) pairs -> (weight, group) lists
  (`tools/re_encounters.py`). warp.lua forces a battle with a READY poke `@1DDF:00gg`.
- Character records `$1900 + slot * $E4` (`01:8B14`): +0/+2/+4 stat words, +9 HP, +B max HP, +D MP, +F max MP,
  **+$CF.. item ids** (one byte per slot, 0 = empty; two herbs bought in a shop wrote `$42` to `$19CF/$19D0`).
  Poking them at READY (`@19CF:4342,...`) gives Kurt that inventory in battle (`battle_routes.tsv` `s*`/`iscroll*`).
  Poking `$3E` = 4 and `$0600-03` = 1 at READY did not add party members to the battle (unit setup reads something
  else; not found yet).
- Battle units `$1298 + i * $28` (party 0-3, enemies from `$1338`; copied by `29:B216`): +E HP, +10 max, +12 MP,
  +14 max, +16/+18/+1A the record's first three stats. GOD gives the party units 999 HP (a refill each frame lost to a
  killing blow); WIN sets their stats to 999 (the level-1 hero does no damage to group `$53` otherwise).
- Loss: "全滅しました・・・", fade, back to the title (no separate game-over screen; `wipeout` scene).
- Win: experience and a **LEVEL UP!!** window with English labels (MAX HP / MAX MP / ...): graphics survey item.

## Scene modes in scenes.tsv (warp.lua)
- room `title`: no boot; keys run from power-on (title, load screen). Room `load`: normal boot, but with a save the
  title defaults to LOAD, so the boot's A taps load FILE1 and the saved room is kept (READY when entered).
- pokes words: `sav=<file>` (run_scenes.py passes `--sav work/saves/<file>`, made by `make_saves.py`), `credits`
  (skip `02:D988` so the staff roll plays), `god`, `win`, `noenc`.

## Modes
- `$0E` game mode, `$10` next mode (`00:9610`: high nibble `$10` = field/menu). Battle sub-states show in `$10`
  only while the engine uses DP 0 as scratch: not a reliable battle flag; use `$1DDF`.

## Menus
- Field menu (A, `01:8145` from `00:916C`): 7 icons, jump table `01:818C`: talk, search, magic, item, status
  (stats + equipment slots + money), tactics (さくせん: choose tactics `01:9B62`?, formation たいれつ), system
  (stereo/mono). Overworld menu (A; the first A after READY is ignored): 5 icons, table `01:813B`: magic, item,
  status, tactics, **camp** (`01:819A`): セーブする / ゲームをおわる (quit: セーブしますか? then title).
- Menu windows and labels are bank-04 scripts (file `0x20400-0x22300`) of BG3 tile words (`<00xx>`) and FA ops:
  this is where the menu labels the text scan missed live (phase 4 extraction). Save labels FILE1 / NEW FILE are
  English tiles already.

## Saving (verified: `tools/debug/save.py`, `tests/test_save.py`, scenes save_* / title_load / stress_money)
- Only on the overworld: camp > セーブする > FILE1/FILE2 > よろしいですか? With a save present the title shows
  NEWGAME/**LOAD** and LOAD is the default (warp.lua's boot then opens the load screen: scene rooms `title`/`load`).
- SRAM service `03:F80B` (A = 0 check slots, 1 save slot `$0884`, 2 load, 3, 4 = new game init). Slot s at
  `$70:s*$1000`: +0 magic "FUCK YOU" (`03:F961`), +8 checksum = 16-bit byte sum of +$0A..+$789, +$0A data (stream
  below, ends at +$544), +$78A backup copy (the loader falls back to it), +$F0A load-screen header: level (`$1922`)
  and name (`$0024`, 8 bytes).
- Stream = descriptor table `03:FBA2` (type, addr, bank, len [+ 3 bytes for type 1]), save handlers `03:FC44`:
  64 gathered bytes (word list `03:FB22`: `$0D24-29` room/x/y, `$0D2A` facing, `$0D3A` music, `$003E` party size,
  `$0600-09` party list, ...); `$1C90-$1DD8` plain (money `$1DD1`, 24-bit, capped 9,999,999 by `01:E255`); name
  `$0024`; story flags `$0200-$04FF` one bit each; four character records `$1900 + i*$E4`, each byte packed to the
  bit width in `03:FA3E`. Packing `03:FD03`: low bits MSB first; the tail is padded by 8-bit ROLs starting with carry
  set and always takes one more byte (a whole extra byte when aligned). Unpack `03:FD6B`.
- The save holds the room and position, so `save.py edit --room R --x X --y Y` loads anywhere.

## Story variants and the ending (verified: scenes variant_* / ending)
- Room load `00:B305`: story flag `$026F` set -> rooms 1, `$1A`, `$88`, `$F8` load blocks 39-42 (top entry 13,
  `01:E5F7`) instead of their own; else `$EC|$EE` = k (1-10) loads block 28+k (top entry 12, `01:E5DA`) when the room
  is `00:B34B[k-1]` (1, `$15`, `$78`, `$89`, `$B9`, `$107`, `$DB`, `$10C`, `$110`, `$F8`). script_dis's rooms 310-323.
- Ending: room 1 + flag `$026F` (block 39): epilogue events, then op **A404** (`01:BC6E`: fade, `JSL 02:D598`):
  `02:D988` epilogue text + "Fin" (tiles), waits on APU port `$2143` bit 1 (`02:DB40`), then `02:D618`/`D6DA` staff
  roll: 24 entries, pointer table `02:E215` -> text `0x16245`, one per `$78` frames (`02:D71F`).
- The chapter 4 title (『第四章 ウ－ドの滅亡』) is NPC dialogue in room 198 (`$7F:015A`), not a card screen; no
  other chapter titles exist in the text.

## Text coverage (verified: `work/qa/cover`, session 23)
- `build.py` writes `build/strings.tsv` (`tools/strings_tsv.py`): ROM strings keyed by the file offset of the first
  byte read (slot, or bank-pool copy), block strings by `1<<40 | stream offset << 16 | offset in block`: every
  script block decompresses over `$7F:0000`, so the key needs the stream.
- `tools/debug/textcover.lua` (after warp.lua): the decompressor `00:83A7` reads its pointers with absolute
  `LDA $00AC..$00B2` (00:83C8; it sets D = `$0100` itself, so the caller's D does not matter): source `$AC-$AE`,
  destination `$B0-$B2`; a destination of `$7F:0000` sets the current stream. Reads of `$7F` and of the ROM banks
  in RANGES log `TEXT <key>`. Session 25 fixes: (1) the E5 common-block call runs with D = `$0C00`, so the old
  DP-relative read never saw the common block (all 33 `common_*` lines unlogged); (2) the LZ decoder's copies read
  its own output (`00:8621`), which logged block strings at decompression time (a frame after `BLOCK`); reads by
  PCs `00:83A7-863C` are now skipped. Every block-key log made before session 25 is unreliable.
- Spells: a character's 12 spell slots are `$1927 + 14i` (01:EEFD): byte 0 bit 7 = known, low 5 bits = spell type
  (22 types, description jump table 01:F6BA), +3 MP, +4 the 8-byte name (`02 n 41`: name n, rank A), +C/+D power.
  Seal items `$F5-$FF` hold one such slot each at `$1CF1 + 14 * (id - $F5)` (01:F413; flag set: the description
  box shows the type's short name from `$04:A7A5`). `names_cover.py spells|spelldesc|sealdesc|itemdesc|examine`.
- RUNS: each entry runs as the field loop runs e1 (`$0634` = 1, VM call `00:D64C` pointed at it); the script has
  ended when the field loop calls `00:D634` again. A place-name label (rooms entered from the map) holds the field
  loop until a button: the probe taps B while a run is armed. A mashed through text; B after 1500 frames backs
  out of shops (E4).
- Names: items, enemies and tactics are keyed by their ROM record's name field (read when a list draws them).
  Spell names live only in the character records in WRAM (copied from the new-game record / joining blocks), so
  their key is the English name in the `$FC:8000` name table (`insert.NameTable`, pointer per kind * 256 + n).
  `tools/debug/names_cover.py` pokes unseen item ids into Kurt's 16 slots (`$19CF`) and opens the item list.
- Session 27 probes: chest messages run the chest op from warp.lua OPS (`00A042` = A0 flag 0 item $42: found;
  `00A1640000` = A1 money 100: Sol; `00A000` item 0: nothing inside; `80A000`: already empty; 16 items poked: no
  room; all four records' slots full and `$3E` = 4: party no room). "File erased" (b04_B966): `load_fail.lua`
  forces the title LOAD's result (01:8387) to fail. Spell types (slot byte 0 low 5 bits) are the 22 distinct spells
  in order of first appearance in spells.json: 0 Fireball ... 7 Restore, 10 Silence, 13 Escape, 15 Teleport.
  The magic healer's menu (E4 07 00, top21) opens with its question: Treat / Combine / Check / Break down.
  **emu.py `--mash` starts at power-on**, not after warp.lua's KEYS, so in a probe it presses A in the menus the
  keys are walking: put the A presses in KEYS instead.
- Any text edit can shift every block stream (session 24: -1 byte), so a coverage set is tied to one build: keep the
  ROM and its `strings.tsv` together (`work/qa/cover_build/`) and run every probe of the set on that ROM.
- `tools/debug/textcover_run.py OUT` runs every room (and the 14 story-variant blocks with their pokes), restarting
  after any entry that leaves the room or sticks. Report: `textcover.py OUT build/strings.tsv --waive
  docs/text_unshown.tsv --mask 0xFFFFFFFFFFFF`.
