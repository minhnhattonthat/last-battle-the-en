"""Every room block and the common block disassemble with no desync (docs/re/text.md); skips without the ROM."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Last Battle, The (Japan).sfc"
sys.path.insert(0, str(ROOT / "tools"))


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM in rom/")
def test_all_scripts_walk_clean():
    import script_dis as sd
    rom = ROM.read_bytes()
    bad = []
    for i in (list(range(sd.ROOM_COUNT + len(sd.EXTRA_ROOMS))) + ["common"]
              + [f"top{n}" for n in sd.COMMON_FORMAT[1:]]):
        _, d = sd.room_block(rom, i)
        res = sd.walk_common(d) if isinstance(i, str) else sd.walk_room(d, i)
        if res[1]:
            bad.append((i, res[1][:2]))
    assert not bad, bad


def test_font_table_is_jis_ordered():
    """tbl/font_jp.tsv: $0384-$07AD strictly increasing in JIS X 0208 (the font is a JIS-ordered subset)."""
    from re_kanji_fix import ORDERED_END, jis
    rows = [ln.split("\t") for ln in (ROOT / "tbl" / "font_jp.tsv").read_text(encoding="utf-8").splitlines()]
    m = {int(c, 16): ch for c, ch in rows}
    assert min(m) == 0x384 and max(m) == 0x7D0 and len(m) == 0x7D1 - 0x384
    assert all(jis(m[c]) > jis(m[c - 1]) for c in range(0x385, ORDERED_END))
