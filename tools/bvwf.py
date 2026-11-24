"""Battle VWF (asm/vwf.asm `bvwf_rect`, docs/re/battle.md §Battle VWF): tables and a model of the renderer.

Battle text is BG3 tile words copied into the WRAM tilemap `$7E:B800`. After a window-script copy from ROM (29:A249),
an escape-message copy (30:F242), the victory line (3C:8000) and the item-found line (30:AD9A), `bvwf_rect` finds
the English runs in each row of the rectangle and redraws each one in proportional type on canvas tiles, BG3 tiles
`BASE..BASE+COUNT-1` (free in battle VRAM: the battle font ends at $119, the status stream starts at $180), then
points the run's cells at them (the cells it no longer needs become spaces). A run is a stretch of text tiles in one
row, single spaces included; two spaces, a non-text tile (border, icon, digit, kanji) or the rectangle's end close it,
so columns that code fills in later (numbers after "MAX HP +") keep their place. Digits stay fixed-width tiles.

Glyphs are the 8x8 BG3 font's own (capitals from LZ block 319, lowercase and punctuation from font_bg3.GLYPHS),
trimmed to their ink, advance = ink width + GAP; space = SPACE_W.

Build outputs (build.py -> apply_asm, incbin'd by asm/vwf.asm):
  build/bvwf_font.bin    96 x 8 bytes, ASCII $20-$7F, row bytes with the ink's left column at bit 7
  build/bvwf_widths.bin  96 advances
  build/bvwf_chars.bin   256 bytes: BG3 tile -> ASCII (0 = not text)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

BASE = 0x11A          # first canvas tile (asm !BV_BASE)
COUNT = 102           # canvas tiles, up to $17F (asm !BV_N)
CHUNK = 16            # tiles per upload descriptor
SPACE = 0x93          # battle space tile
SPACE_W = 4
GAP = 1
# Blank pad glyphs, width -> (BG3 tile, ASCII slot). Each row of a typed message (battle_text.column_messages) starts
# with one in an extra cell left of the message, so the proportional row sits centred where the JP centred its
# kanji. Tiles: kanji of those messages' old columns, read by nothing since they became English (keep_jp.txt);
# ASCII slots the font leaves free. The asm only adds a glyph's width to the pen, so a pad may be wider than a cell.
PADS = {13: (0xF9, "{"), 16: (0xFB, "|"), 19: (0x97, "}"), 22: (0xF3, "~")}
MAX_RUN = 32          # chars per run the asm buffers (a row is at most 32 cells)
CAPITALS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def glyph_rows(orig):
    """{char: 8 ints (bit 7 = left pixel)} for digits, capitals and the font_bg3 characters (ink = plane 1)."""
    import blocks
    import font_bg3
    d = font_bg3.patch(blocks.unpack(orig).blocks[font_bg3.BLOCK].data)
    out = {}
    for i, c in enumerate(CAPITALS):
        t = 1 + i
        out[c] = [d[t * 16 + 2 * y + 1] for y in range(8)]
    for c, t in font_bg3.TILE.items():
        out[c] = [d[t * 16 + 2 * y + 1] for y in range(8)]
    return out


def trimmed(rows):
    """(rows shifted so the leftmost ink column is bit 7, ink width)."""
    ink = 0
    for r in rows:
        ink |= r
    if not ink:
        return [0] * 8, 0
    left = max(b for b in range(8) if ink >> b & 1)      # highest set bit = leftmost column
    right = min(b for b in range(8) if ink >> b & 1)
    sh = 7 - left
    return [(r << sh) & 0xFF for r in rows], left - right + 1


def tables(orig):
    """(font 96*8, widths 96, chars 256) bytes."""
    rows = glyph_rows(orig)
    font, widths = bytearray(96 * 8), bytearray(96)
    for c, r in rows.items():
        g, w = trimmed(r)
        i = ord(c) - 0x20
        font[i * 8:i * 8 + 8] = bytes(g)
        widths[i] = w + GAP
    widths[0] = SPACE_W
    chars = bytearray(256)
    for i, c in enumerate(CAPITALS[10:]):
        chars[0x0B + i] = ord(c)
    import font_bg3
    for c, t in font_bg3.TILE.items():
        chars[t] = ord(c)
    chars[SPACE] = 0x20
    for w, (t, c) in PADS.items():
        assert not chars[t] and c not in rows, (hex(t), c)
        chars[t], widths[ord(c) - 0x20] = ord(c), w
    return bytes(font), bytes(widths), bytes(chars)


def pad_for(widths, text, cells):
    """The PADS width that centres `text` (ink width) in `cells` fixed cells, counted from the cell before them."""
    ink = width(widths, text) - GAP
    return min(PADS, key=lambda p: abs(p - 8 - (8 * cells - ink) / 2))


def write(orig, outdir=ROOT / "build"):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    font, widths, chars = tables(orig)
    (outdir / "bvwf_font.bin").write_bytes(font)
    (outdir / "bvwf_widths.bin").write_bytes(widths)
    (outdir / "bvwf_chars.bin").write_bytes(chars)


def runs(cells):
    """Model of the asm's run scan. cells = one row, each an ASCII char or None (not text) ->
    [(first cell, last cell, text)]."""
    out, i, n = [], 0, len(cells)
    while i < n:
        c = cells[i]
        if c is None or c == " ":
            i += 1
            continue
        start = last = i
        s = ""
        while i < n and cells[i] is not None and len(s) < MAX_RUN:
            if cells[i] == " ":
                if i + 1 >= n or cells[i + 1] in (None, " "):
                    break
            else:
                last = i
            s += cells[i]
            i += 1
        out.append((start, last, s.rstrip(" ")))
        i = last + 1
    return out


def width(widths, text):
    return sum(widths[ord(c) - 0x20] for c in text)


def overflow(widths, cells):
    """Runs in a row whose proportional width is more than their cells hold: [(text, px, cells)]."""
    return [(s, width(widths, s), last - first + 1) for first, last, s in runs(cells)
            if width(widths, s) > 8 * (last - first + 1)]
