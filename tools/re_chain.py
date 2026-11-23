"""Recon: enumerate LZ blocks by chaining (block end = next block start) from seed offsets, e.g. the sources
logged by tools/lua/decomp_src.lua. A block is accepted when its header is sane (u16 L, then u16 L-2 or a size
no larger than 64 KB) and it decompresses without running more than 16 KB past its stated stream size.

    python -X utf8 tools/re_chain.py SEED [SEED ...] [--out work/chain.tsv] [--dump DIR]
    python -X utf8 tools/re_chain.py --log work/qa/decsrc/log.txt     # seeds from a decomp_src.lua log
Writes TSV rows: offset, compressed size, decompressed size, seed.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from lz import decompress  # noqa: E402


def try_block(rom, off):
    if off + 4 > len(rom):
        return None
    hdr = rom[off] | rom[off + 1] << 8
    second = rom[off + 2] | rom[off + 3] << 8
    if hdr < 4 or second != hdr - 2:
        return None
    try:
        data, size = decompress(rom, off)
    except Exception:  # noqa: BLE001 - recon: not a block
        return None
    if not data or size != hdr + 2:
        return None
    return data, size


def chain(rom, seed, known):
    off, n = seed, 0
    while off not in known:
        r = try_block(rom, off)
        if r is None:
            break
        known[off] = (r[1], len(r[0]), seed)
        off += r[1]
        n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seeds", nargs="*")
    ap.add_argument("--log")
    ap.add_argument("--out", default="work/chain.tsv")
    ap.add_argument("--dump")
    ap.add_argument("--scan", action="store_true", help="scan the whole ROM for block headers")
    a = ap.parse_args()
    rom = (ROOT / "rom" / "Last Battle, The (Japan).sfc").read_bytes()
    seeds = [int(s, 16) for s in a.seeds]
    if a.log:
        seeds += [int(m, 16) for m in re.findall(r"\(off ([0-9A-F]{6})\)", Path(a.log).read_text())]
    known = {}
    if a.scan:  # every offset whose header matches and whose stream is exactly L+2 bytes, then chain from it
        p = 0
        while p < len(rom) - 4:
            if (rom[p] | rom[p + 1] << 8) - 2 == (rom[p + 2] | rom[p + 3] << 8) >= 2 and p not in known:
                r = try_block(rom, p)
                if r and len(r[0]) >= 32:
                    chain(rom, p, known)
                    p += r[1]
                    continue
            p += 1
    for s in sorted(set(seeds)):
        chain(rom, s, known)
    rows = sorted(known.items())
    Path(ROOT / a.out).write_text("".join(f"{o:06X}\t{c}\t{d}\t{s:06X}\n" for o, (c, d, s) in rows))
    tot_c = sum(c for c, _, _ in known.values())
    print(f"{len(rows)} blocks, {tot_c} compressed bytes -> {a.out}")
    if a.dump:
        out = ROOT / a.dump
        out.mkdir(parents=True, exist_ok=True)
        for o, _ in rows:
            (out / f"{o:06X}.bin").write_bytes(decompress(rom, o)[0])


if __name__ == "__main__":
    main()
