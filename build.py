"""build.py: build build/lastbattle_en.sfc from the dump in rom/ (SHA-1 in rom.sha1, checked first).

Pipeline: unpack the LZ block region and its pointer tables (tools/blocks.py) -> apply edits (none yet: phase 4+)
-> repack. Every write goes through put(), which refuses offsets outside tools/ranges.txt and logs
`OFFSET ORIG_HEX NEW_HEX writer` to build/writes.txt; romdiff.py then checks the output against the original with
that log (wrong original bytes, overlapping or overwritten writes, a changed byte no write explains).

With no edits the output is byte-identical to the original (tests/test_identity.py).

    python -X utf8 build.py [--out FILE] [--recompress]
--recompress runs every block through lz.compress (blocks move; the game must still run): a relocation check."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import blocks  # noqa: E402
import check_rom  # noqa: E402
import romdiff  # noqa: E402

ORIG_PATH = ROOT / "rom" / "Last Battle, The (Japan).sfc"
OUT = ROOT / "build" / "lastbattle_en.sfc"


def load_ranges(path=ROOT / "tools" / "ranges.txt"):
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        lo, _, hi = line.split()[0].partition("-")
        out.append((int(lo, 16), int(hi or lo, 16) + 1))
    return out


class Writer:
    """The one way to change the ROM: checks the range, logs the original bytes it replaces."""

    def __init__(self, orig, ranges):
        self.orig = orig
        self.rom = bytearray(orig)
        self.ranges = ranges
        self.log = []

    def put(self, off, data, by):
        end = off + len(data)
        if not any(lo <= off and end <= hi for lo, hi in self.ranges):
            raise ValueError(f"{by}: write 0x{off:06X}-0x{end - 1:06X} is outside tools/ranges.txt")
        if self.rom[off:end] == data:
            return
        old = self.orig[off:end].ljust(len(data), b"\xff")
        self.log.append((off, old, bytes(data), by))
        self.rom[off:end] = data


def build(out=OUT, recompress=False, orig_path=ORIG_PATH):
    orig = orig_path.read_bytes()
    w = Writer(orig, load_ranges())
    region = blocks.unpack(orig)
    region.pack(w.rom, w.put, recompress=recompress)
    rom = bytes(w.rom)
    errs, _ = romdiff.check(orig, rom, [], w.log)
    if errs:
        raise SystemExit("romdiff:\n" + "\n".join(errs))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(rom)
    lines = [f"{o:X} {a.hex()} {b.hex()} {by}" for o, a, b, by in w.log]
    out.with_name("writes.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8", newline="\n")
    return rom, w.log


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--recompress", action="store_true")
    a = ap.parse_args()
    check_rom.check()
    rom, log = build(a.out, a.recompress)
    import hashlib
    print(f"{a.out}: {len(rom)} bytes, {len(log)} writes, sha1 {hashlib.sha1(rom).hexdigest()}")


if __name__ == "__main__":
    main()
