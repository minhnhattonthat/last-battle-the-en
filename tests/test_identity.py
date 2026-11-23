"""Identity build (phase 3): unpack -> repack with no edits gives the original ROM byte for byte; with every block
recompressed (they move), or one block edited, every pointer slot still decodes to the right data.
Builds its own ROM into a temp dir; skips without the ROM."""
import os
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Last Battle, The (Japan).sfc"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import lz  # noqa: E402

need_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM in rom/")


def test_compress_roundtrip_synthetic():
    rnd = random.Random(1)
    cases = [b"", b"\x00", b"\x00" * 5000, b"ab" * 3000, b"abc" * 9, bytes(range(256)) * 12,
             bytes(rnd.randrange(4) for _ in range(6000)), os.urandom(3000), b"\x12\x34\x56\x78" * 700]
    for data in cases:
        s = lz.compress(data)
        got, size = lz.decompress(s, 0)
        assert got == data and size == len(s)


@need_rom
def test_identity_build(tmp_path):
    import build
    rom, log = build.build(tmp_path / "id.sfc", asm=False, jp_only=True)
    assert log == []
    assert rom == ROM.read_bytes()
    assert (tmp_path / "id.sfc").read_bytes() == rom


def _decode_all(rom):
    import blocks
    out = {}
    for slot in blocks.slots():
        f = blocks.to_file(blocks.read_ptr(rom, slot))
        if blocks.REGION_START <= f < blocks.REGION_END and not any(a <= f < b for a, b in blocks.FIXED):
            out[slot] = lz.decompress(rom, f)[0]
    return out


@need_rom
def test_recompress_relocates(tmp_path):
    import build
    orig = ROM.read_bytes()
    rom, log = build.build(tmp_path / "re.sfc", recompress=True, asm=False, jp_only=True)
    assert log, "recompressing should move blocks"
    want = _decode_all(orig)
    got = _decode_all(rom)
    assert got.keys() == want.keys()
    assert len({orig[s:s + 3] for s in want}) == 324  # every block is reached through some slot
    for slot, data in want.items():
        assert got[slot] == data, hex(slot)
    # outside the block region and tables nothing moved
    assert rom[:0xD0000] == orig[:0xD0000] and rom[0x107CF3:] == orig[0x107CF3:]
    assert rom[0x1068B9:0x1068F9] == orig[0x1068B9:0x1068F9]


@need_rom
def test_edit_one_block():
    import blocks
    import build
    orig = ROM.read_bytes()
    w = build.Writer(orig, build.load_ranges())
    region = blocks.unpack(orig)
    b = region.blocks[5]
    b.data = b.data + b"\xff\x00" * 40
    region.pack(w.rom, w.put)
    rom = bytes(w.rom)
    errs, _ = build.romdiff.check(orig, rom, [], w.log)
    assert errs == []
    got = _decode_all(rom)
    want = _decode_all(orig)
    for slot, data in want.items():
        expect = b.data if slot in b.slots else data
        assert got[slot] == expect, hex(slot)
