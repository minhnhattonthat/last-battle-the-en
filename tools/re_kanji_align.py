"""re_kanji_align.py: identify the katakana/kanji glyphs of the ROM font by monotonic alignment to JIS X 0208.

The font is a JIS-ordered subset (docs/re/text.md) up to $07AD; $07AE-$07D0 are extra kanji out of order (staff
names for the credits). For the ordered part glyph i maps to JIS character j(i) with j strictly increasing: each
game glyph is scored against every candidate rendered from reference fonts (bbox-centred, blurred, cosine), then a
DP picks the increasing assignment with the best total. The tail gets the free best match.

    python -X utf8 tools/re_kanji_align.py [--out work/kanji_align.tsv]
Output TSV: code, aligned char, score, free best char, its score, runner-up in the allowed window, margin.
Check rows where aligned != free best or the margin is small by eye (tools/re_glyphs.py)."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from re_glyphs import ROM, glyph

ROOT = Path(__file__).resolve().parents[1]
FONTS = ["C:/Windows/Fonts/msgothic.ttc", "C:/Windows/Fonts/YuGothM.ttc"]
LO, ORDERED_END, HI = 0x384, 0x7AE, 0x7D1


def jis_candidates():
    rows = [0x25] + list(range(0x30, 0x75))  # katakana, level-1 and level-2 kanji
    out = []
    for r in rows:
        for c in range(0x21, 0x7F):
            try:
                ch = bytes([r | 0x80, c | 0x80]).decode("euc_jp")
            except UnicodeDecodeError:
                continue
            if len(ch) == 1 and ch not in out:
                out.append(ch)
    return out


def vec(a):
    """binary image -> bbox-centred 24x24, blurred, unit-norm vector."""
    ys, xs = np.nonzero(a)
    c = np.zeros((24, 24))
    if len(xs):
        cy, cx = (ys.min() + ys.max()) // 2, (xs.min() + xs.max()) // 2
        for y, x in zip(ys, xs):
            yy, xx = y - cy + 12, x - cx + 12
            if 0 <= yy < 24 and 0 <= xx < 24:
                c[yy, xx] = 1
    k = np.array([1, 2, 1], float) / 4
    for ax in (0, 1):
        c = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), ax, c)
    v = c.ravel()
    return v / (np.linalg.norm(v) or 1)


def ref_vecs(cands, size, path):
    font = ImageFont.truetype(path, size)
    out = np.zeros((len(cands), 576))
    for j, ch in enumerate(cands):
        im = Image.new("L", (40, 40), 0)
        ImageDraw.Draw(im).text((10, 10), ch, font=font, fill=255)
        out[j] = vec(np.asarray(im) > 96)
    return out


def align(S):
    """S[i, j] score; maximise the sum with j strictly increasing. Returns j per i."""
    n, m = S.shape
    best = np.full((n, m), -1e9)
    back = np.zeros((n, m), int)
    best[0] = S[0]
    for i in range(1, n):
        prev = best[i - 1]
        arg = np.zeros(m, int)
        cur = 0
        for j in range(m):
            if prev[j] > prev[cur]:
                cur = j
            arg[j] = cur
        best[i, 1:] = S[i, 1:] + prev[arg[:-1]]
        back[i, 1:] = arg[:-1]
    j = int(best[-1].argmax())
    path = [j]
    for i in range(n - 1, 0, -1):
        j = back[i, j]
        path.append(j)
    return path[::-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "work" / "kanji_align.tsv"))
    a = ap.parse_args()
    rom = ROM.read_bytes()
    codes = list(range(LO, HI))
    G = np.array([vec(np.array(glyph(rom, c, rowfmt="tltr")) > 0) for c in codes])
    cands = jis_candidates()
    S = None
    for path in FONTS:
        for size in (12, 13, 14, 15, 16):
            s = G @ ref_vecs(cands, size, path).T
            S = s if S is None else np.maximum(S, s)
    n_ord = ORDERED_END - LO
    path = align(S[:n_ord]) + [int(S[i].argmax()) for i in range(n_ord, len(codes))]
    rows, flagged = [], 0
    for i, (c, j) in enumerate(zip(codes, path)):
        free = int(S[i].argmax())
        if i < n_ord:
            lo = path[i - 1] + 1 if i else 0
            hi = path[i + 1] if i + 1 < n_ord else len(cands)
        else:
            lo, hi = 0, len(cands)
        win = [(S[i, k], k) for k in range(lo, hi) if k != j]
        ru = max(win) if win else (0.0, j)
        margin = S[i, j] - ru[0]
        flagged += free != j or margin < 0.01
        rows.append(f"{c:04X}\t{cands[j]}\t{S[i, j]:.3f}\t{cands[free]}\t{S[i, free]:.3f}\t{cands[ru[1]]}\t{margin:.3f}")
    Path(a.out).write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(a.out, len(rows), "glyphs;", flagged, "flagged (aligned != free best or margin < 0.01)")


if __name__ == "__main__":
    main()
