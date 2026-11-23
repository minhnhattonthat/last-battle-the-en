"""Recon: decode the 1-byte name encoding (01:FEE3): byte b >= $2C -> glyph word at $04:B053 + 2*(b - $2C)
(file 0x23053), 0 ends. Item records (01:8B2D): 20 bytes, name in the first 8; index < $C0 at $04:CAD1
(file 0x24AD1), index >= $C0 at $04:D201 (file 0x25201).

    python -X utf8 tools/re_names.py items            # every item record's name
    python -X utf8 tools/re_names.py scan [--min 3]   # find runs of name-encoded bytes anywhere in the ROM
    python -X utf8 tools/re_names.py at 24AD1 20 8 COUNT   # records at OFFSET, STRIDE, NAMELEN, COUNT
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from re_textscan import ROM, load_names, word_text  # noqa: E402

MAP_OFF, MAP_FIRST = 0x23053, 0x2C


def byte_map(rom, names):
    """{byte: text} for every byte whose table word is a glyph."""
    out = {}
    for b in range(MAP_FIRST, 0x100):
        p = MAP_OFF + 2 * (b - MAP_FIRST)
        w = rom[p] | rom[p + 1] << 8
        if 0x300 <= w <= 0x7D0:
            out[b] = word_text(w, names)
    return out


def decode(rom, bm, off, n):
    s = []
    for b in rom[off:off + n]:
        if b == 0:
            break
        s.append(bm.get(b, f"<{b:02X}>"))
    return "".join(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["items", "scan", "at", "map"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--min", type=int, default=3)
    a = ap.parse_args()
    rom = ROM.read_bytes()
    bm = byte_map(rom, load_names())
    if a.cmd == "map":
        print(" ".join(f"{b:02X}={t}" for b, t in sorted(bm.items())))
    elif a.cmd == "items":
        for i in range(0x100):
            off = 0x24AD1 + 20 * i if i < 0xC0 else 0x25201 + 20 * (i - 0xC0)
            print(f"{i:02X} {off:06X} {decode(rom, bm, off, 8)}")
    elif a.cmd == "at":
        off, stride, n, count = (int(x, 16) if k == 0 else int(x) for k, x in enumerate(a.args))
        for i in range(count):
            print(f"{i:02X} {off + stride * i:06X} {decode(rom, bm, off + stride * i, n)}")
    else:
        i = 0
        while i < len(rom):
            j = i
            while j < len(rom) and rom[j] in bm:
                j += 1
            if j - i >= a.min and (j >= len(rom) or rom[j] == 0):
                print(f"{i:06X} {j - i:3d} {decode(rom, bm, i, j - i)}")
            i = j + 1


if __name__ == "__main__":
    main()
