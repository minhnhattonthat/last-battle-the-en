"""blocks.py: unpack and repack the LZ block region and its pointer tables (docs/re/compression.md).

Layout of the original ROM:
  0xD0000  top table, 43 x 24-bit linear pointers (file = ptr - 0xD8000). Entries 10/12/13 point back into the top
           table itself (sub-table aliases); 0 points at the room table; 1, 7, 8, 9 at non-LZ data.
  0xD0081  room table, 309 x 24-bit linear pointers.
  0xD0420  324 LZ blocks back to back up to the font at 0x107CF3, with the 64-byte top-entry-1 data at 0x1068B9.
Every block is reached by at least one slot of the two tables; no code or data elsewhere holds a block address
(whole-ROM scan for the 24-bit forms, 2026-11-23: 35 hits, all inside instruction pairs or graphics/LZ data).

unpack(rom) -> Region; region.pack(rom, put) writes the blocks back into the free areas in their original order and
rewrites every slot. A block whose data is unchanged keeps its original compressed bytes (lz.compress is a valid
encoder but not the original tool's parse), so a no-edit pack is byte-identical. pack(..., recompress=True) runs
every block through lz.compress instead: the relocation test.

python -X utf8 tools/blocks.py dump [DIR]   writes every decompressed block + manifest.tsv (default work/unpack)."""
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lz  # noqa: E402

LINEAR_BASE = 0xD8000          # file = linear - LINEAR_BASE (01:FDDF)
TOP, TOP_N = 0xD0000, 43
ROOMS, ROOMS_N = 0xD0081, 309
REGION_START, REGION_END = 0xD0420, 0x107CF3
FIXED = [(0x1068B9, 0x1068F9)]  # top entry 1: raw data inside the block run, stays put
FREE = [(0xD0420, 0x1068B9), (0x1068F9, 0x107CF3)]
# 4 MB build: blocks that no longer fit go past 0x200000 (FDDF maps linear pointers there, banks $40-$7C).
# 0x300000-0x3DFFFF holds moved strings (insert.TEXT_AREA), 0x3E8000+ ($FD:8000) asm/vwf.asm.
EXPANSION = (0x200000, 0x300000)


def to_file(ptr):
    return ptr - LINEAR_BASE


def to_ptr(off):
    return off + LINEAR_BASE


def read_ptr(rom, slot):
    return int.from_bytes(rom[slot:slot + 3], "little")


def slots():
    """Every pointer slot (file offset) of the top and room tables."""
    return [TOP + 3 * i for i in range(TOP_N)] + [ROOMS + 3 * i for i in range(ROOMS_N)]


@dataclass
class Block:
    index: int        # order in the original ROM
    orig_off: int
    orig_stream: bytes  # header + commands, as in the original
    orig_data: bytes
    data: bytes       # edit this
    slots: list       # pointer slots that reach it

    @property
    def w1(self):
        return int.from_bytes(self.orig_stream[2:4], "little")

    def stream(self, recompress=False):
        if self.data == self.orig_data and not recompress:
            return self.orig_stream
        L = len(self.orig_stream) - 2
        # 322 blocks store L - 2 here; rooms 20 and 264 store the decompressed size. lz.py's model of 00:83A7
        # ignores the word (guess: unused); keep each block's convention anyway.
        if self.w1 == L - 2:
            return lz.compress(self.data)
        assert self.w1 == len(self.orig_data), (self.index, self.w1)
        return lz.compress(self.data, len(self.data))


@dataclass
class Region:
    blocks: list

    def by_off(self):
        return {b.orig_off: b for b in self.blocks}

    def pack(self, rom, put, recompress=False, free=FREE):
        """Write every block into the free areas in order, then every slot. put(off, data, by) logs each write."""
        areas = [list(a) for a in free]
        a = 0
        placed = {}
        for b in self.blocks:
            s = b.stream(recompress)
            while a < len(areas) and areas[a][0] + len(s) > areas[a][1]:
                a += 1
            if a == len(areas):
                raise ValueError(f"block {b.index} ({len(s)} bytes) does not fit: no free area left")
            off = areas[a][0]
            put(off, s, f"block{b.index:03d}")
            placed[b.index] = off
            areas[a][0] += len(s)
        for start, end in areas:  # unused tails (the expansion stays 0xFF)
            if start < end and start < EXPANSION[0] and any(rom[start:end]):
                put(start, bytes(end - start), "block-free")
        for b in self.blocks:
            for slot in b.slots:
                new = to_ptr(placed[b.index]).to_bytes(3, "little")
                if rom[slot:slot + 3] != new:
                    put(slot, new, f"ptr{b.index:03d}")
        return placed


def unpack(rom):
    """Decompress the block run; attach each pointer slot to its block. Asserts the layout described above."""
    blocks = []
    off = REGION_START
    fixed = dict(FIXED)
    while off < REGION_END:
        if off in fixed:
            off = fixed[off]
            continue
        data, size = lz.decompress(rom, off)
        blocks.append(Block(len(blocks), off, bytes(rom[off:off + size]), data, data, []))
        off += size
    assert off == REGION_END, hex(off)
    starts = {b.orig_off: b for b in blocks}
    for slot in slots():
        f = to_file(read_ptr(rom, slot))
        if f in starts:
            starts[f].slots.append(slot)
    missing = [b.index for b in blocks if not b.slots]
    assert not missing, f"blocks with no pointer: {missing}"
    return Region(blocks)


def kind(rom, b):
    """A label for the manifest: which table slots reach the block."""
    names = []
    for s in b.slots:
        names.append(f"top{(s - TOP) // 3}" if s < ROOMS else f"room{(s - ROOMS) // 3}")
    return ",".join(names)


def dump(rom, out):
    out.mkdir(parents=True, exist_ok=True)
    region = unpack(rom)
    rows = ["index\toff\tcomp\tsize\tw1\tslots"]
    for b in region.blocks:
        (out / f"{b.index:03d}_{b.orig_off:06X}.bin").write_bytes(b.data)
        rows.append(f"{b.index}\t{b.orig_off:06X}\t{len(b.orig_stream)}\t{len(b.data)}\t{b.w1}\t{kind(rom, b)}")
    (out / "manifest.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(region.blocks)} blocks -> {out}")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    if len(sys.argv) >= 2 and sys.argv[1] == "dump":
        rom = (root / "rom" / "Last Battle, The (Japan).sfc").read_bytes()
        dump(rom, Path(sys.argv[2]) if len(sys.argv) > 2 else root / "work" / "unpack")
    else:
        print(__doc__)
