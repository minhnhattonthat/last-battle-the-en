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
- Character records `$1900 + slot * $E4` (`01:8B14`): +0/+2/+4 stat words, +9 HP, +B max HP, +D MP, +F max MP.
- Battle units `$1298 + i * $28` (party 0-3, enemies from `$1338`; copied by `29:B216`): +E HP, +10 max, +12 MP,
  +14 max, +16/+18/+1A the record's first three stats. GOD gives the party units 999 HP (a refill each frame lost to a
  killing blow); WIN sets their stats to 999 (the level-1 hero does no damage to group `$53` otherwise).
- Loss: "全滅しました・・・", fade, back to the title (no separate game-over screen; `wipeout` scene).
- Win: experience and a **LEVEL UP!!** window with English labels (MAX HP / MAX MP / ...): graphics survey item.

## Modes
- `$0E` game mode, `$10` next mode (`00:9610`: high nibble `$10` = field/menu). Battle sub-states show in `$10`
  only while the engine uses DP 0 as scratch: not a reliable battle flag; use `$1DDF`.

## Not found yet (carried in status.md)
- **Saving.** No save prompt in any script or bank-04 text; SRAM (`$70:0000-1FFF`) is written only at boot
  (`03:F9xx`, signature check) in every route so far. Save-slot display code exists (`01:E725`/`E7D7` = FA00/FA25
  menu ops, reads `$70:0F0A`; `JSL 03:F80B`), used by bank-04 window templates around file `0x21AD4-0x21D30`
  (pointer table at `$04:82B6+`). Next: find what opens those windows (title CONTINUE? an NPC?), then save.py.
- Menu windows and labels are bank-04 scripts (file `0x20400-0x22300`) of BG3 tile words (`<00xx>`) and FA ops:
  this is where the menu labels the text scan missed live (phase 4 extraction).
