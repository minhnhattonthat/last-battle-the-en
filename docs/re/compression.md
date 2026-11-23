# Compression and block pointers

## LZ format (verified on one block; roundtrip test still to write)
Decompressor `00:83A7` (source `$AC-$AE`, dest `$B0-$B2`, DP `$0100`), byte reader `00:8417` (walks LoROM banks:
after `$FFFF` it goes to the next bank at `$8000`). Python: `tools/lz.py` (`decompress(rom, off) -> (data, size)`).
- Header: u16 L, u16 (= L-2 in the block checked). The stream is L+2 bytes in total, header included.
- Ring buffer 2 KB at `$7E6280`, zeroed at start, position 0; every output byte is written to it.
- `c < $80`: back-reference. b = next byte, w = c<<8|b, length = (b & 15) + 2, distance = (w >> 4) & $7FF.
  The run is read from the ring in full **before** it is written back (`00:8607` then `00:861F`), so an overlapping
  run repeats stale ring bytes. Emulated in `lz.py`.
- `$80-$BF`: literal run of (c & $3F) + 1 bytes.
- `$C0-$FF`: fill. n = c & 7, or (c & 7) << 8 | next byte when c & $20; n += 2. Pattern width
  ((c >> 3) & 3) + 1 bytes follows; written n times.
- verified by: block at file 0xD3772 (the first room's script) equals WRAM `$7F0000` for the 3150 bytes the game
  had written at the dump frame (`work/qa/dec3`, from `work/qa/play1/s001000.mss` + mash A, frame 270). Phase 3 needs a
  full-WRAM check after the load finishes, then a recompressor with a byte-exact identity test.

## Block pointers (verified for one entry)
- Pointers are 24-bit **linear** addresses, converted by `01:FDDF`: file = 0xD0000 + (ptr - $1A8000)
  (font base `$1DFCF3` -> 0x107CF3, room script `$1AB772` -> 0xD3772).
- Table region `0xD0000-0xD0420` (`$1A:8000`): top table of 43 3-byte pointers at 0xD0000. Entry 0 -> room table
  0xD0081 (309 entries, to 0xD0420); 10 -> 0xD002A (= top entries 14-28), 12 -> 0xD0057 (= 29-38), 13 -> 0xD0075
  (= 39-42): sub-tables that alias the top table. 7 = font (`$1A:8015`), 11 = common script block (read at
  `$1A:8021` by E5), 29-42 = room-format blocks, 14-28 = other formats (18/19 plain text, 20-27 tables; to map),
  1-6, 8, 9 = graphics/other. Which code reads 1-6, 8-10, 14-28: still to map.
- Blocks: 324 back-to-back LZ blocks from 0xD0420 to 0x107CF3 (one 64-byte non-block gap at 0x1068B9-0x1068F9).
  The font (uncompressed) follows at 0x107CF3. Entry 9 at 0x111817 is something else (followed by 26 KB of zeros).
- Relocation: blocks can move anywhere in the linear space as long as the pointer is rewritten; a block may cross
  a bank (the reader handles it). Pointers above `$1B0000` are linear, so moved blocks just need linear addresses.

## Free space
Runs of `$00` >= 1 KB (`python -X utf8 tools/re_trap.py` lists them and writes `work/trap.sfc` with each filled
with `$FF`): 0x6F26 (4130), 0x16877 (6025), 0x27BE9 (1047), 0x2B5A0 (19040), 0x542F4 (15628), 0xC8F5D (28835),
0x111837 (26569), 0x11B8C8 (1848), 0x13DCC6 (9018).
- Trap test (2026-11-23): the trap ROM plays the boot route, name entry and the first room's events (7000 frames,
  mash A) with the same screens as the original (`work/qa/trap1` vs `work/qa/orig_play`; runs of the same ROM are not
  frame-identical, compared by eye), and `tools/lua/trap_reads.lua` logged **0 CPU reads** in any candidate over that
  run (positive control: 54 reads of the name-entry prompt range). **Verified only for that route**: re-run
  `trap_reads.lua` on the phase-2 debug-tool tour before putting anything there.
- 0x111817 (top entry 9) is 32 bytes of data followed by this zero run; `lz.py` "decompresses" 14 KB from it only
  because zeros decode as back-references: it is not an LZ block.
- **Preferred for new data: expand to 4 MB** (header `$7FD7` = `$0C`): clean space past 0x200000, reached by the
  linear pointer scheme (`FDDF` keeps adding banks) and by long addressing for code. Needs a check that the mapper
  mirrors nothing there (phase 5).
