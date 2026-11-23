"""Graphics-text static sweep, part 2: pack every decompressed LZ block that looks like tile graphics
(work/chain/*.bin from re_chain.py --dump) into labelled sheets for reading by eye.

    python -X utf8 tools/re_blocksheets.py [--fmt snes4|snes2] [--out work/sweep/blocks] [--zoom 2] [--list]

Each block: a label line "OFFSET fmt" then its tiles, 32 per row. Blocks skipped (score too high = not tiles,
or too small) are printed with the reason, never dropped silently.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
PC = [bin(i).count("1") for i in range(256)]


def score(d):
    """Mean bit change between a tile row and the next row of the same plane (2 bytes on): ~4 for random data,
    low for tile graphics."""
    n = len(d) - 2
    if n <= 0:
        return 9
    ks = [k for k in range(n) if k % 16 < 14]
    return sum(PC[d[k] ^ d[k + 2]] for k in ks) / max(1, len(ks))


def tile_pixels(d, off, fmt):
    px = []
    for y in range(8):
        row = []
        for x in range(8):
            bit = 7 - x
            v = (d[off + 2 * y] >> bit & 1) | (d[off + 2 * y + 1] >> bit & 1) << 1
            if fmt == "snes4":
                v |= (d[off + 16 + 2 * y] >> bit & 1) << 2 | (d[off + 17 + 2 * y] >> bit & 1) << 3
            row.append(v)
        px.append(row)
    return px


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fmt", default="snes4", choices=["snes4", "snes2"])
    ap.add_argument("--out", default="work/sweep/blocks")
    ap.add_argument("--zoom", type=int, default=2)
    ap.add_argument("--max-score", type=float, default=2.6)
    ap.add_argument("--height", type=int, default=1400)
    ap.add_argument("--only", help="file listing block offsets (hex) to include")
    a = ap.parse_args()
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    tb = 32 if a.fmt == "snes4" else 16
    maxv = 15 if a.fmt == "snes4" else 3
    cols, z = 32, a.zoom
    W = cols * 8 * z
    sheets, cur, y, index = [], None, 0, []
    files = sorted((ROOT / "work" / "chain").glob("*.bin"))
    if a.only:
        keep = set(Path(a.only).read_text().split())
        for f in files:
            if f.stem not in keep:
                print(f"skip {f.stem}: not in {a.only} (script area, overlapping chain or oversized)")
        files = [f for f in files if f.stem in keep]
    for f in files:
        d = f.read_bytes()
        s = score(d)
        if len(d) > 0x10000:
            print(f"skip {f.stem}: {len(d)} bytes decompressed, more than 64 KB (false header match)")
            continue
        if len(d) < 4 * tb or s > a.max_score:
            print(f"skip {f.stem}: {len(d)} bytes, score {s:.2f}")
            continue
        n = len(d) // tb
        rows = (n + cols - 1) // cols
        h = 12 + rows * 8 * z
        if cur is None or y + h > a.height:
            cur = Image.new("L", (W, max(a.height, h)), 40)
            sheets.append(cur)
            y = 0
        dr = ImageDraw.Draw(cur)
        dr.text((2, y), f"{f.stem} {a.fmt} {len(d)}B s={s:.2f}", fill=255)
        for t in range(n):
            px = tile_pixels(d, t * tb, a.fmt)
            tx, ty = (t % cols) * 8 * z, y + 12 + (t // cols) * 8 * z
            for yy in range(8):
                for xx in range(8):
                    c = 255 - px[yy][xx] * 255 // maxv
                    if c != 255:
                        dr.rectangle([tx + xx * z, ty + yy * z, tx + xx * z + z - 1, ty + yy * z + z - 1], fill=c)
                    else:
                        dr.rectangle([tx + xx * z, ty + yy * z, tx + xx * z + z - 1, ty + yy * z + z - 1],
                                     fill=255)
        index.append((len(sheets) - 1, f.stem))
        y += h + 4
    for i, im in enumerate(sheets):
        im.save(out / f"{a.fmt}_{i:03d}.png")
    (out / f"{a.fmt}_index.tsv").write_text("".join(f"{i:03d}\t{b}\n" for i, b in index))
    print(f"{len(index)} blocks on {len(sheets)} sheets -> {a.out}")


if __name__ == "__main__":
    main()
