"""tools/debug/save.py: the bit packer matches the game's, the descriptor table is the ROM's, and a game-written save
round-trips byte for byte and survives edits (fixture: tests/fixtures/base_file1.srm, FILE1 written by the game
in the save_done scene). The in-game load of an edited save is checked by the stress_money scene + save_check.lua."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Last Battle, The (Japan).sfc"
FIXTURE = ROOT / "tests" / "fixtures" / "base_file1.srm"
sys.path.insert(0, str(ROOT / "tools" / "debug"))
import save  # noqa: E402

needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM in rom/")


def test_pack_unpack_inverse():
    widths = [8, 2, 3, 7, 1, 8, 5]
    vals = [0xA5, 2, 5, 0x41, 1, 0xFF, 17]
    b = save.pack_bits(vals, widths)
    assert len(b) == sum(widths) // 8 + 1
    got, pos = save.unpack_bits(b, 0, widths)
    assert got == vals and pos == len(b)


def test_pack_aligned_writes_extra_byte():
    # 16 bits end on a byte boundary: the game still writes a third byte: 8 ROLs of the 9-bit ring carry:$34 with
    # carry set (= the ring 0x134 rotated right once) leave $9A
    assert save.pack_bits([0x12, 0x34], [8, 8]) == bytes([0x12, 0x34, 0x9A])


@needs_rom
def test_descriptor_table_matches_rom():
    d = ROM.read_bytes()
    o = save.lorom(3, 0xFBA2)
    got = []
    while (d[o] | d[o + 1] << 8) != 0xFF:
        t, addr, ln = d[o] | d[o + 1] << 8, d[o + 2] | d[o + 3] << 8, d[o + 5] | d[o + 6] << 8
        o += 7 + (3 if t == 1 else 0)
        got.append(({2: "gather", 0: "plain", 3: "bits1", 1: "record"}[t], 0 if t == 2 else addr, ln))
    assert got == save.SECTIONS


@needs_rom
def test_game_save_roundtrips_and_edits():
    raw = FIXTURE.read_bytes()
    sv = save.Save(raw, 0)
    assert sv.build() == raw
    assert sv.end <= save.DATA + save.DATA_LEN
    sv.set(0x1DD1, 0x7F); sv.set(0x1DD2, 0x96); sv.set(0x1DD3, 0x98)
    sv.set(0x200 + 0x6F, 1)
    out = sv.build()
    again = save.Save(out, 0)
    assert save.money(again) == 9999999 and again.ram[0x26F] == 1
    assert out[0x78A:0x78A + 0x780] == out[0x0A:0x0A + 0x780]
    with pytest.raises(ValueError):
        sv.set(0x200, 2)  # a story flag is one bit
