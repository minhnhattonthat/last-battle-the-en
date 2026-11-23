"""font_en.py: the English VWF font (tools/font_en.txt) -> build/font_en.bin + build/font_en_widths.bin.

font_en.txt (own design, docs/fonts.md): one block per glyph, "= c" ("= space" for the blank), then rows of '#'
(ink) and '.' drawn from cell row TOP down, then an optional "w N" line setting the advance (default: width + 1).
Output, indexed by ASCII code 0-127 (script word $0800 + code, tools/textcodec.py EN):
- font_en.bin: 16 bytes per glyph, one byte per pixel row 0-15, bit 7 = leftmost column (asm/vwf.asm);
- font_en_widths.bin: the advance in px per glyph.
Ink is at most 8 px wide (the VWF draws one byte per row). The fit lint reads ADVANCE from here.

    python -X utf8 tools/font_en.py [OUTDIR]"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tools" / "font_en.txt"
TOP = 3  # cell row of the first font_en.txt row (cap height rows TOP..TOP+8, descenders TOP+9..TOP+10)


def parse(path=SRC):
    glyphs, cur = {}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("#") and cur is None or not line:
            continue
        if line.startswith("= "):
            name = line[2:]
            ch = " " if name == "space" else name
            assert len(ch) == 1, line
            cur = glyphs[ch] = {"rows": [], "adv": None}
        elif line.startswith("w "):
            cur["adv"] = int(line[2:])
        else:
            assert set(line) <= {"#", "."}, line
            cur["rows"].append(line)
    for ch, g in glyphs.items():
        w = max((len(r) for r in g["rows"]), default=0)
        assert w <= 8, f"{ch!r}: {w} px wide > 8"
        assert TOP + len(g["rows"]) <= 16, f"{ch!r}: {len(g['rows'])} rows from row {TOP} pass the cell"
        g["width"] = w
        g["adv"] = g["adv"] if g["adv"] is not None else w + 1
    return glyphs


GLYPHS = parse()
ADVANCE = {ch: g["adv"] for ch, g in GLYPHS.items()}


def build():
    font, widths = bytearray(16 * 128), bytearray(128)
    for ch, g in GLYPHS.items():
        c = ord(ch)
        assert 0x20 <= c < 0x7F, ch
        for r, row in enumerate(g["rows"]):
            font[16 * c + TOP + r] = sum(0x80 >> i for i, p in enumerate(row) if p == "#")
        widths[c] = g["adv"]
    return bytes(font), bytes(widths)


def write(outdir=ROOT / "build"):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    font, widths = build()
    (outdir / "font_en.bin").write_bytes(font)
    (outdir / "font_en_widths.bin").write_bytes(widths)


def width(text_chars):
    """Advance in px of a run of plain characters."""
    return sum(ADVANCE[c] for c in text_chars)


if __name__ == "__main__":
    write(*sys.argv[1:])
    print(f"{len(GLYPHS)} glyphs")
