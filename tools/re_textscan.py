"""Recon: find runs of script text (glyph words $0300-$07D0, with FE/FF/FA controls) anywhere in the ROM and in
every LZ block the top table or room table points at.

    python -X utf8 tools/re_textscan.py [--min 3] [--raw-only | --blocks-only] [--range 20000 28000] [--show N]

A run = consecutive 16-bit LE words, each a glyph or one of the controls that occur inside plain strings (FExx,
FFxx, FAxx, A4xx). Both byte alignments are scanned. Prints one line per run: where, length, decoded text.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lz import decompress  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / "rom" / "Last Battle, The (Japan).sfc"
GLYPH_MAX = 0x07D0
INLINE_OPS = {0xFE, 0xFF, 0xFA}


def load_names():
    names = {}
    for line in (ROOT / "tbl" / "jp.tbl").read_text(encoding="utf-8").splitlines():
        key, sep, val = line.partition("=")
        if line.startswith("#") or not sep or len(key) != 4:
            continue
        names[int.from_bytes(bytes.fromhex(key), "little")] = " " if val == r"\s" else val
    return names


def kana_share(words):
    """Share of glyph words that are kana ($0334-$03D5): real text is mostly kana, random data is not."""
    g = [w for w in words if 0x301 <= w <= GLYPH_MAX]
    return sum(0x334 <= w <= 0x3D5 for w in g) / len(g) if g else 0


def word_text(w, names):
    if 0x300 <= w <= GLYPH_MAX:
        ch = names.get(w, f"[{w:04X}]")
        return "　" if w == 0x300 else ch
    op, lo = w >> 8, w & 0xFF
    if op == 0xFE:
        return "/" if lo == 0 else f"{{FE{lo:02X}}}"
    if op == 0xFF:
        return f"{{FF{lo:02X}}}"
    return f"{{{w:04X}}}"


def runs(d, min_glyphs=3):
    """Yield (start, end, glyph count, words) for each run in d, both alignments, runs not overlapping a longer
    run at the other alignment."""
    found = []
    for align in (0, 1):
        i = align
        start, words, g = None, [], 0
        while i + 1 < len(d) + 1:
            w = d[i] | d[i + 1] << 8 if i + 1 < len(d) else -1
            ok = 0x300 <= w <= GLYPH_MAX or (w >= 0x8000 and (w >> 8) in INLINE_OPS)
            if ok:
                if start is None:
                    start, words, g = i, [], 0
                words.append(w)
                g += w < 0x8000 and w != 0x300
            if not ok or i + 3 >= len(d) + 1:
                if start is not None and g >= min_glyphs:
                    found.append((start, start + 2 * len(words), g, words))
                start = None
                if not ok and i + 3 >= len(d) + 1:
                    break
            i += 2
            if i + 1 >= len(d):
                if start is not None and g >= min_glyphs:
                    found.append((start, start + 2 * len(words), g, words))
                break
    found.sort(key=lambda r: (-r[2], r[0]))
    taken, out = [], []
    for r in found:
        if any(r[0] < t[1] and t[0] < r[1] for t in taken):
            continue
        taken.append(r)
        out.append(r)
    return sorted(out)


def lin2off(p):
    return 0xD0000 + (p - 0x1A8000)


def blocks(rom):
    seen = {}
    for i in range(43):
        p = int.from_bytes(rom[0xD0000 + 3 * i:0xD0003 + 3 * i], "little")
        seen.setdefault(lin2off(p), f"top{i}")
    for i in range(309):
        p = int.from_bytes(rom[0xD0081 + 3 * i:0xD0084 + 3 * i], "little")
        seen.setdefault(lin2off(p), f"room{i}")
    for off, name in sorted(seen.items()):
        if off in (0xD0081, 0xD002A, 0xD0057, 0xD0075, 0x107CF3) or not 0xD0420 <= off < 0x107CF3:
            continue
        try:
            data, csize = decompress(rom, off)
        except Exception as e:  # noqa: BLE001 - recon: report and go on
            print(f"# {name} {off:06X}: not LZ ({e})")
            continue
        yield name, off, data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=3)
    ap.add_argument("--raw-only", action="store_true")
    ap.add_argument("--blocks-only", action="store_true")
    ap.add_argument("--range", nargs=2, default=None)
    ap.add_argument("--skip-rooms", action="store_true", help="skip room-format blocks (walked by script_dis.py)")
    ap.add_argument("--show", type=int, default=60, help="characters of text shown per run")
    ap.add_argument("--kana", type=float, default=0.5, help="minimum kana share of a raw run (noise filter)")
    a = ap.parse_args()
    rom = ROM.read_bytes()
    names = load_names()
    if not a.blocks_only:
        lo, hi = (int(a.range[0], 16), int(a.range[1], 16)) if a.range else (0, len(rom))
        # skip the LZ block area and the font: compressed bytes and glyph bitmaps give noise
        for s, e, g, words in runs(rom[lo:hi], a.min):
            s += lo
            e += lo
            if 0xD0420 <= s < 0x111713 or kana_share(words) < a.kana:
                continue
            txt = "".join(word_text(w, names) for w in words)
            print(f"raw {s:06X}-{e:06X} g={g:4d} {txt[:a.show]}")
    if not a.raw_only:
        for name, off, data in blocks(rom):
            if a.skip_rooms and name.startswith("room") or (a.skip_rooms and name in
                                                            {f"top{i}" for i in [11] + list(range(29, 43))}):
                continue
            for s, e, g, words in runs(data, a.min):
                txt = "".join(word_text(w, names) for w in words)
                print(f"{name}@{off:06X} {s:04X}-{e:04X} g={g:4d} {txt[:a.show]}")


if __name__ == "__main__":
    main()
