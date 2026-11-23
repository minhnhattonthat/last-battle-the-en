# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| `text.md` | header, encoding (16-bit words), font layout and JIS-subset order, control codes, where text lives, extraction | encoding, font, control-code walk and extraction (roundtrip + coverage tests) verified; control-code meanings partly provisional |
| `compression.md` | LZ format + compressor, linear block pointers, unpack/repack (`tools/blocks.py`), free-space candidates | verified: identity build + relocated build (phase 3); what top entries 1-6, 8-10, 14-28 hold partly mapped |
| `graphics.md` | graphics-text survey | started (boot screens only) |
| `battle.md` | battle names (enemies, tactics, spell windows: 29:B2B6), battle font + battle LZ (`tools/blz.py`), battle message survey | names + font verified on the marker build; battle messages surveyed, not extracted |
| `debug.md` | map-change request, script injection, battle trigger and units, RAM used by `tools/debug/warp.lua` | verified by the scene runs; saving not found |
