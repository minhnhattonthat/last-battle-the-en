# English text engine (phase 5): VWF, far jumps, 4 MB

Source: `asm/vwf.asm` (asar 1.91 in `tools/asar/`, applied by `build.py` after the text is inserted), font
`tools/font_en.txt` -> `tools/font_en.py` -> `build/font_en.bin` + `build/font_en_widths.bin`.

## Layout (verified: build + boot)
- ROM expanded to 4 MB (header `$7FD7` = `$0C`; the release step fixes the checksum).
- `0x200000-0x2FFFFF`: LZ blocks that no longer fit the original area (`blocks.EXPANSION`; FDDF maps the linear
  pointers there, LoROM banks `$40-$5F`). `0x300000-0x3DFFFF`: moved strings (`insert.TEXT_AREA`, never across a
  32 KB bank). `0x3E8000` (`$FD:8000`): code + font. Banks `$7E/$7F` (file `0x3F0000+`) are WRAM: unusable.
- WRAM `$7EFFF0-$7EFFF5`: VWF state (next to the debug tool's `$7EFF00` op buffer; both zero in every dump).

## Glyph renderer (01:B882, verified by reading the code and in-game shots)
The game draws a 16x16 1bpp glyph (copied to `$7E2620` as TL, TR, BL, BR) into a 4-tile 2bpp buffer `$7E2F40`
(TL `$2F40`, TR `$2F50`, BL `$2F60`, BR `$2F70`); NMI (01:B630) uploads TL+TR to VRAM word `$0C30` and BL+BR to
`$0C30+$100`. Originally 12 px per glyph: `$0C24` = even/odd phase, `$0C20` (VRAM word of the left column) steps 8 or
16, 01:B859 shifts TR->TL after an even glyph. Text modes `$0C2A`: 0 = ink plane 1 on a plane-0 background, 1 =
plane 1 only, 2 = both planes. Line starts: FE00 sets `$0C20 = $6600 + line * $200` and `$0C24 = 0`; FB (window open)
and 01:AFEE, 01:BCDC reset them; 01:B13C sets `$0C24 = $5C` (window width) for windowed runs.
Callers: dialogue (01:B81F: draw, upload flag `$0C1E`, wait `$2C`+1 frames, B859) and the menu string drawer
01:B467 (draws each glyph, copies TL/TR to `$7E6C80 + 2 * $0C20` and BL/BR to `$6E80 + ...`, then B859).

## VWF (asm/vwf.asm)
`$0C24` becomes the pixel offset inside the buffer's left column. A glyph is ORed in at that offset; its advance is
added; the upload target `$0C30` = `$0C20`. After the upload, `vwf_post` (01:B859) shifts out each full 8 px
column, adding 8 to `$0C20`. The buffer is cleared when `$0C24` = 0 or `$0C20` differs from the column last drawn.
Words `$0800-$087F` = English (ASCII = word - `$0800`, `textcodec.EN`); `$0300-$07FF` keep the Japanese font at a
12 px advance (identical shots to the original: name entry, item menu, status). Font cell rows: `font_en.TOP`.

## Far jumps (tools/insert.py)
Word `$F700` + 24-bit CPU address. Strings keep their slot size: a longer English string moves to `TEXT_AREA` and
its slot becomes a far jump there (rest zero), the moved copy ending in a far jump back to the byte after the slot
(`$7F:addr` for blocks, which all run at `$7F0000`; the bank for bank 04 / credits). A shorter one is padded with
up to 2 spaces, or ends in a far jump over the rest. So no block image or bank-04 address changes and no pointer
needs rewriting. Readers that follow it: the script VM (control dispatch 01:BA96) and the menu string drawer (01:B485).
Strings shorter than 5 bytes can't hold a jump: `r095_00FE` (「) and `b04_B2E2` (メイ, a 16-bit pointer `0x232D4`).

## Hooks
| Site | Was | Why |
|---|---|---|
| 01:B89B | PLA / SEC / SBC #$0300 | glyph fetch: English words read `font_en` |
| 01:B8C9 | even/odd dispatch | VWF draw |
| 01:B859 | shift on even glyph, INC $24 | shift full columns after the upload |
| 01:B13C | LDA $5C / STA $24 | odd window width = 4 px start offset |
| 01:BA96 | PHP / REP / XBA / PHA | control dispatch: far jump F7 |
| 01:B485 | LDA [$10] / CMP #$FF00 | menu string fetch: far jump |
| 02:D7A8 | LDA [$B2],y / CMP #$FE00 | staff roll fetch: far jump |
| 02:D7F9 | PHA / LDA $1A8015 | staff roll glyph: English VWF (`cr_glyph`) |

## Staff roll (bank 02, verified: `credits` scene on the marker and ruler builds)
02:D71F draws entry `$C2` (pointer table `02:E215`, bank `$B4` = 2) with 02:D789: clears the 2bpp tile image
`$7E6C80` (`$1400` bytes, DMA'd to VRAM `$6000`), X = `$10`, then per word: FE00 = X += `$400` (next 32 px slot), FF00
= end, else 02:D7F9 draws a 16x16 glyph at tile column X (`$10` bytes per tile, 16 tiles per row, rows 8-15 `$100`
on; wrap: low byte 0 -> +`$110`), 12 px packing with `$B8` bit 0. `cr_glyph` ORs English glyphs at pixel P of
column X (P = 4 if `$B8` is odd, else `$B8`/2; stores `$B8` = P*2), plane 0 only, as the game does. WRAM
`$7EFFF6-$7EFFFD`. The game's per-glyph call to 02:D7CD (fiddles `$08BB`) is skipped for English.
