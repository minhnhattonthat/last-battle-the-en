"""re_glyphs.py: render 16x16 1bpp glyphs from the ROM font as a zoomed, labelled sheet (recon helper).

    python -X utf8 tools/re_glyphs.py OUT.png CODE [CODE...]       # codes in hex
    python -X utf8 tools/re_glyphs.py OUT.png --range 300 340       # code range [lo, hi)
Glyph address: FONT_BASE + code * 32 (see docs/re/text.md). --base / --rowfmt to try other layouts."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Last Battle, The (Japan).sfc"
FONT_BASE = 0x101CF3


def glyph(rom, code, base=FONT_BASE, rowfmt="interleaved"):
    g = rom[base + code * 32: base + code * 32 + 32]
    px = []
    for y in range(16):
        t = y // 8
        if rowfmt == "interleaved":  # 2 bytes per row, left then right
            w = (g[2 * y] << 8) | g[2 * y + 1]
        elif rowfmt == "tltr":  # four 8x8 1bpp tiles: TL, TR, BL, BR
            w = (g[2 * t * 8 + y % 8] << 8) | g[(2 * t + 1) * 8 + y % 8]
        elif rowfmt == "tlbl":  # four 8x8 1bpp tiles: TL, BL, TR, BR
            w = (g[t * 8 + y % 8] << 8) | g[(t + 2) * 8 + y % 8]
        else:  # left 8x16 column then right 8x16 column
            w = (g[y] << 8) | g[16 + y]
        px.append([(w >> (15 - x)) & 1 for x in range(16)])
    return px


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("codes", nargs="*")
    ap.add_argument("--range", nargs=2)
    ap.add_argument("--base", default=hex(FONT_BASE))
    ap.add_argument("--rowfmt", default="interleaved", choices=["interleaved", "columns", "tltr", "tlbl"])
    ap.add_argument("--cols", type=int, default=16)
    a = ap.parse_args()
    rom = ROM.read_bytes()
    codes = [int(c, 16) for c in a.codes]
    if a.range:
        codes += list(range(int(a.range[0], 16), int(a.range[1], 16)))
    z, cw, ch = 3, 16 * 3 + 6, 16 * 3 + 16
    rows = (len(codes) + a.cols - 1) // a.cols
    im = Image.new("RGB", (a.cols * cw, rows * ch), (40, 40, 60))
    d = ImageDraw.Draw(im)
    for i, c in enumerate(codes):
        x0, y0 = (i % a.cols) * cw, (i // a.cols) * ch
        for y, row in enumerate(glyph(rom, c, int(a.base, 16), a.rowfmt)):
            for x, p in enumerate(row):
                if p:
                    d.rectangle([x0 + 3 + x * z, y0 + y * z, x0 + 3 + x * z + z - 1, y0 + y * z + z - 1], fill=(255, 255, 255))
        d.text((x0 + 3, y0 + 16 * z + 2), f"{c:04X}", fill=(255, 220, 80))
    im.save(a.out)
    print(a.out, len(codes), "glyphs")


if __name__ == "__main__":
    main()
