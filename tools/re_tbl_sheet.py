"""re_tbl_sheet.py: proof sheet for a glyph -> char mapping: each ROM glyph (zoom 2) above the char it is mapped to,
rendered from MS Gothic, with the code. Mismatches stand out when the two shapes differ.

    python -X utf8 tools/re_tbl_sheet.py MAP.tsv OUT_PREFIX [--per 500] [--cols 36] [--only 42E 444 ...]
MAP.tsv: code<TAB>char per line (extra columns ignored), e.g. work/kanji_align.tsv."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from re_glyphs import ROM, glyph


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("map")
    ap.add_argument("out")
    ap.add_argument("--per", type=int, default=500)
    ap.add_argument("--cols", type=int, default=36)
    ap.add_argument("--only", nargs="*", help="hex codes to keep")
    a = ap.parse_args()
    rom = ROM.read_bytes()
    rows = [ln.split("\t")[:2] for ln in Path(a.map).read_text(encoding="utf-8").splitlines() if ln.strip()]
    if a.only:
        keep = {int(c, 16) for c in a.only}
        rows = [r for r in rows if int(r[0], 16) in keep]
    font = ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", 26)
    small = ImageFont.load_default()
    cw, ch = 40, 76
    for p in range(0, len(rows), a.per):
        part = rows[p:p + a.per]
        nr = (len(part) + a.cols - 1) // a.cols
        im = Image.new("RGB", (a.cols * cw, nr * ch), (30, 30, 45))
        d = ImageDraw.Draw(im)
        for i, (code, char) in enumerate(part):
            x0, y0 = (i % a.cols) * cw, (i // a.cols) * ch
            for y, r in enumerate(glyph(rom, int(code, 16), rowfmt="tltr")):
                for x, v in enumerate(r):
                    if v:
                        d.rectangle([x0 + 4 + 2 * x, y0 + 2 * y, x0 + 5 + 2 * x, y0 + 1 + 2 * y], fill=(255, 255, 255))
            d.text((x0 + 5, y0 + 33), char, font=font, fill=(120, 230, 255))
            d.text((x0 + 4, y0 + 62), code, font=small, fill=(255, 210, 80))
        out = f"{a.out}_{p // a.per}.png"
        im.save(out)
        print(out, len(part))


if __name__ == "__main__":
    main()
