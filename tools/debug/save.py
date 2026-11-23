"""Save editor for The Last Battle (SNES battery save, 8 KB SRAM, 2 files).

    python -X utf8 tools/debug/save.py dump  SRM [--slot 0]
    python -X utf8 tools/debug/save.py edit  SRM OUT [--slot 0] [--money N] [--poke ADDR=HEX].. [--flag N=0|1]..
                                             [--room R --x X --y Y] [--level-hdr N]

Format (03:F80B SRAM service, layout in docs/re/debug.md "Saving"): slot s at file offset s * 0x1000:
  +0x000  magic "FUCK YOU" (03:F961)
  +0x008  checksum: 16-bit sum of the bytes +0x00A..+0x789
  +0x00A  data A (0x780 bytes): a stream built from the descriptor table at 03:FBA2 (see SECTIONS)
  +0x78A  data B: copy of data A (the loader falls back to it when A's sum fails)
  +0xF0A  load-screen header: level byte ($1922), name 8 bytes ($0024)
Every value is a WRAM address ($7E0000 + addr). The game loads the save by unpacking the stream back into WRAM, so
any address the stream covers can be edited here: money $1DD1 (24-bit), name $0024, story flags $0200-$04FF (one bit
each), the four character records $1900 + i*$E4 (fields packed to the widths in 03:FA3E), room/x/y $0D24/26/28.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROM = ROOT / "rom" / "Last Battle, The (Japan).sfc"
MAGIC = b"FUCK YOU"
SLOT_SIZE = 0x1000
DATA, DATA_LEN, BACKUP, HDR = 0x0A, 0x780, 0x78A, 0xF0A


def lorom(bank, addr):
    return (bank & 0x7F) * 0x8000 + (addr - 0x8000)


def rom_tables(rom):
    """Gather list (64 WRAM addresses, 0 = unused byte) and the character-record bit widths."""
    g = lorom(3, 0xFB22)
    gather = [rom[g + 2 * i] | rom[g + 2 * i + 1] << 8 for i in range(64)]
    w = lorom(3, 0xFA3E)
    widths = list(rom[w:w + 0xE4])
    return gather, widths


# The descriptor table at 03:FBA2, as decoded from the ROM (asserted by tests/test_save.py):
#   (kind, wram, length): gather = byte list, plain = copy, bits1 = 1 bit per byte, record = widths table.
SECTIONS = [("gather", 0, 64), ("plain", 0x1C90, 0x149), ("plain", 0x0024, 8), ("bits1", 0x0200, 0x300),
            ("record", 0x1900, 0xE4), ("record", 0x19E4, 0xE4), ("record", 0x1AC8, 0xE4), ("record", 0x1BAC, 0xE4)]


def pack_bits(values, widths):
    """03:FD03: low `width` bits of each value, MSB first; the tail byte is padded by 8-bit ROLs that start with
    carry set (the loop's final CMP), and a whole extra byte is written when the bits end on a byte boundary."""
    out = bytearray()
    acc, left = 0, 8
    for v, n in zip(values, widths):
        for k in range(n - 1, -1, -1):
            acc = ((acc << 1) | ((v >> k) & 1)) & 0xFF
            left -= 1
            if left == 0:
                out.append(acc)
                left = 8
    carry = 1
    for _ in range(left):
        acc, carry = ((acc << 1) | carry) & 0xFF, acc >> 7
    out.append(acc)
    return bytes(out)


def unpack_bits(buf, pos, widths):
    """03:FD6B: inverse of pack_bits; returns (values, new pos)."""
    acc = buf[pos]
    pos += 1
    left = 8
    vals = []
    for n in widths:
        v = 0
        for _ in range(n):
            v = (v << 1) | (acc >> 7)
            acc = (acc << 1) & 0xFF
            left -= 1
            if left == 0:
                acc = buf[pos]
                pos += 1
                left = 8
        vals.append(v)
    return vals, pos


class Save:
    """One slot, unpacked to {wram address: byte}."""

    def __init__(self, srm, slot=0, rom=None):
        self.srm = bytearray(srm)
        self.slot = slot
        rom = rom if rom is not None else ROM.read_bytes()
        self.gather, self.widths = rom_tables(rom)
        base = slot * SLOT_SIZE
        self.base = base
        s = self.srm
        if bytes(s[base:base + 8]) != MAGIC:
            raise ValueError(f"slot {slot}: no save (magic missing)")
        stored = s[base + 8] | s[base + 9] << 8
        if self.sum_a() != stored:
            raise ValueError(f"slot {slot}: checksum {self.sum_a():04X} != stored {stored:04X}")
        self.ram = {}
        self.widths_at = {}
        p = base + DATA
        for kind, addr, n in SECTIONS:
            if kind == "gather":
                for i, a in enumerate(self.gather):
                    if a:
                        self.ram[a] = s[p + i]
                p += n
            elif kind == "plain":
                for i in range(n):
                    self.ram[addr + i] = s[p + i]
                p += n
            else:
                w = [1] * n if kind == "bits1" else self.widths
                vals, p = unpack_bits(s, p, w)
                for i, v in enumerate(vals):
                    self.ram[addr + i] = v
                    self.widths_at[addr + i] = w[i]
        self.end = p - base

    def sum_a(self):
        b = self.base + DATA
        return sum(self.srm[b:b + DATA_LEN]) & 0xFFFF

    def set(self, addr, value):
        if addr not in self.ram:
            raise KeyError(f"${addr:04X} is not in the save stream")
        n = self.widths_at.get(addr, 8)
        if value >> n:
            raise ValueError(f"${addr:04X} holds {n} bits; {value:#x} does not fit")
        self.ram[addr] = value

    def build(self):
        s = bytearray(self.srm)
        p = self.base + DATA
        for kind, addr, n in SECTIONS:
            if kind == "gather":
                for i, a in enumerate(self.gather):
                    if a:
                        s[p + i] = self.ram[a]
                p += n
            elif kind == "plain":
                for i in range(n):
                    s[p + i] = self.ram[addr + i]
                p += n
            else:
                w = [1] * n if kind == "bits1" else self.widths
                b = pack_bits([self.ram[addr + i] for i in range(n)], w)
                s[p:p + len(b)] = b
                p += len(b)
        b = self.base
        total = sum(s[b + DATA:b + DATA + DATA_LEN]) & 0xFFFF
        s[b + 8], s[b + 9] = total & 0xFF, total >> 8
        s[b + BACKUP:b + BACKUP + DATA_LEN] = s[b + DATA:b + DATA + DATA_LEN]
        s[b + HDR] = self.ram[0x1922]
        s[b + HDR + 1:b + HDR + 9] = bytes(self.ram[0x24 + i] for i in range(8))
        return bytes(s)


def money(sv):
    return sv.ram[0x1DD1] | sv.ram[0x1DD2] << 8 | sv.ram[0x1DD3] << 16


def word(sv, a):
    return sv.ram[a] | sv.ram[a + 1] << 8


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dump")
    d.add_argument("srm")
    d.add_argument("--slot", type=int, default=0)
    e = sub.add_parser("edit")
    e.add_argument("srm")
    e.add_argument("out")
    e.add_argument("--slot", type=int, default=0)
    e.add_argument("--money", type=int)
    e.add_argument("--poke", action="append", default=[], help="ADDR=HEXBYTES, little-endian bytes from ADDR")
    e.add_argument("--flag", action="append", default=[], help="N=0|1: story flag $0200+N")
    e.add_argument("--room", type=lambda x: int(x, 0))
    e.add_argument("--x", type=lambda x: int(x, 0))
    e.add_argument("--y", type=lambda x: int(x, 0))
    a = ap.parse_args()
    sv = Save(Path(a.srm).read_bytes(), a.slot)
    if a.cmd == "dump":
        name = bytes(sv.ram[0x24 + i] for i in range(8)).hex(" ")
        print(f"slot {a.slot}: stream ends at +{sv.end:#x} (limit {DATA + DATA_LEN:#x})")
        print(f"room {word(sv, 0xD24)} x {word(sv, 0xD26)} y {word(sv, 0xD28)} facing {word(sv, 0xD2A)}")
        print(f"party size {word(sv, 0x3E)} list {[sv.ram[0x600 + i] for i in range(10)]}")
        print(f"money {money(sv)}  name bytes {name}")
        print(f"flags set: {[i for i in range(0x300) if sv.ram[0x200 + i]]}")
        for c in range(4):
            r = 0x1900 + c * 0xE4
            print(f"record {c}: level {sv.ram[r + 0x22]} HP {word(sv, r + 9)}/{word(sv, r + 0xB)} "
                  f"MP {word(sv, r + 0xD)}/{word(sv, r + 0xF)}")
        return
    if a.money is not None:
        m = max(0, min(a.money, 9999999))
        for i in range(3):
            sv.set(0x1DD1 + i, (m >> (8 * i)) & 0xFF)
    for p in a.poke:
        addr, hexb = p.split("=")
        addr = int(addr, 16)
        for i, b in enumerate(bytes.fromhex(hexb)):
            sv.set(addr + i, b)
    for f in a.flag:
        n, v = f.split("=")
        sv.set(0x200 + int(n, 0), int(v))
    for addr, v in ((0xD24, a.room), (0xD26, a.x), (0xD28, a.y)):
        if v is not None:
            sv.set(addr, v & 0xFF)
            sv.set(addr + 1, v >> 8)
    out = sv.build()
    Save(out, a.slot)  # re-parse: magic and checksum must hold
    Path(a.out).write_bytes(out)
    print(f"wrote {a.out}: slot {a.slot}, money {money(sv)}, room {word(sv, 0xD24)}")


if __name__ == "__main__":
    sys.exit(main())
