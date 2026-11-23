"""LZ blocks chain back to back over the script region (docs/re/compression.md); skips without the ROM."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Last Battle, The (Japan).sfc"
sys.path.insert(0, str(ROOT / "tools"))


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM in rom/")
def test_blocks_chain_to_font():
    from lz import decompress
    rom = ROM.read_bytes()
    off, n = 0xD0420, 0
    while off < 0x107CF3:
        if off == 0x1068B9:  # 64-byte non-block gap
            off = 0x1068F9
            continue
        data, size = decompress(rom, off)
        assert data and 4 < size < 0x10000, hex(off)
        off += size
        n += 1
    assert off == 0x107CF3 and n == 324
