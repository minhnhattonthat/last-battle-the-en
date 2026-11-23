# Graphics-text survey (phase 1, in progress)

Every screen with Japanese (or English that needs no change) drawn as tiles rather than through the text engine.
Columns: screen, how reached, layer, first guess at the source.

| Screen | Reached | Layer | Japanese? | Source guess |
|---|---|---|---|---|
| Teichiku logo | boot f300 | BG | English already | - |
| Title logo "The Last Battle", PUSH START / NEWGAME, ©1994 TEICHIKU | boot f600-900 | BG/sprites | English already (D5: keep logo) | - |
| Name entry: kana grid (アイウエオ / あいうえお ... arrows, `E_D` end key) | boot route + A | BG3 window | yes | glyph words from the byte map at `0x23053` (text engine, not graphics) |
| Name entry: second screen shows "SAT ADA..." in Latin | `work/qa/play1` f1600 | BG3 | mixed | text engine |
| In-room dialogue window | `work/qa/play1` f2000+ | BG3 bitmap canvas | yes (text engine) | not graphics |
| BG3 tile strings, 12-byte rows at `0x22CA7` (01:FABC, `$04:ACA7` + 12n) | not yet seen on screen | BG3 | probably (pre-drawn labels) | BG3 chr tiles; find which chr block holds tiles `$26-$13D` |

Still to survey by tour (needs the phase-2 debug tool): field menu, status, items, equipment, shops, battle screen
(commands, messages), save/load, game over, chapter cards, ending, credits, and the screen that uses `0x22CA7`.

## Static sweep (prepared, not yet read)
- `python -X utf8 tools/re_sweep.py`: whole ROM as 2bpp sheets (`work/sweep/raw_XXXXXX_snes2.png`, 0x20000 bytes
  each, 64 tiles per row, zoom 1) plus top-table blocks 2-6 and 8 decompressed (`top<N>_{snes2,snes4,1bpp}.png`).
- Graphics-like regions (row-to-row bit change within tiles, 1 KB granularity): raw `0x30000-0x54000`,
  `0x5F000-0x62000`, `0x108000-0x111000` (= the dialogue font), parts of `0x140000-0x1A0000`, `0x1D7000`,
  `0x1DF000`, `0x1F0000-0x1F3800`. Everything else is code, script or LZ-compressed. `work/sweep/rawg/raw4_*.png`
  renders the raw ones as 4bpp zoom 2: **0x30000 is not legible as 4bpp**, so the format there is unknown (try
  2bpp/8bpp/mode-7, or find it from a VRAM dump with `vramfind.py`).
- The script LZ codec (`tools/lz.py`) also packs graphics: `tools/lua/decomp_src.lua` on the boot + first-room run
  logged sources in banks `$03`, `$0D`, `$13` (file 0x18FFC.., 0x6842D.., 0x9E491..). Logged sources are the read
  pointer when the destination crosses a page, so mid-stream ones are not block starts.
- `python -X utf8 tools/re_chain.py --scan --dump work/chain`: every offset with the header signature
  (u16 L, u16 L-2, stream exactly L+2 bytes) chained forward: 935 matches, many false positives (they overlap,
  decompress to > 64 KB, or sit inside raw graphics). `work/chain_clean.txt` keeps non-overlapping ones outside the
  script area; `tools/re_blocksheets.py --only work/chain_clean.txt` packs the 535 tile-like ones into 21 labelled
  4bpp sheets `work/sweep/blocks/snes4_NNN.png` (index `snes4_index.tsv`; skips printed in `work/sweep_blocks.log`).
  Sheet 000 (blocks in 0x30000-0x54000) is mostly stripes: false positives in raw graphics.
- **Better route than reading 70 sheets by eye:** on each screen the tour reaches, dump VRAM (`ppudump.lua`),
  `tiles.py map` the BG layers, and `vramfind.py` the text tiles against the ROM and `work/chain/*.bin`; then read
  only the sheets of blocks that feed VRAM (`decomp_src.lua` log, dest = VRAM upload buffer).
