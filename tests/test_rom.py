"""The dump in rom/ is the one in rom.sha1 (skips on a clone without the ROM)."""
import hashlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Last Battle, The (Japan).sfc"


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM in rom/")
def test_rom_sha1():
    want = [l.split()[0] for l in (ROOT / "rom.sha1").read_text().splitlines() if l and not l.startswith("#")][0]
    assert hashlib.sha1(ROM.read_bytes()).hexdigest() == want


def test_skill_tools_present():
    for name in ("tbl.py", "bps.py", "romdiff.py", "check_rom.py", "skill.py"):
        assert (ROOT / "tools" / name).is_file(), name
