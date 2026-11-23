"""Phase 5 engine pieces that need no ROM: font widths, the EN codec, far-jump fitting (tools/insert.py fit)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font_en  # noqa: E402
import insert  # noqa: E402
from textcodec import EN  # noqa: E402


def test_font_covers_ascii_and_fits_one_byte():
    assert {chr(c) for c in range(0x20, 0x7F)} <= set(font_en.GLYPHS)
    assert all(g["width"] <= 8 for g in font_en.GLYPHS.values())
    font, widths = font_en.build()
    assert len(font) == 16 * 128 and widths[ord("A")] == font_en.ADVANCE["A"]


def test_en_codec_roundtrip():
    s = "Kurt, it's {actor}!{nl}Go.{page}"
    assert EN.decode(EN.encode(s)) == s
    assert EN.encode("A") == (0x0841).to_bytes(2, "little")


class W:
    def __init__(self):
        self.puts = []

    def put(self, off, data, by):
        self.puts.append((off, data))


def test_fit_same_pad_jump_move():
    w, a = W(), insert.TextAlloc((0x307FF8, 0x310000))
    two = EN.encode("ab")
    assert insert.fit(two, 4, 0x7F1234, a, w, "x") == two
    assert insert.fit(two, 8, 0x7F1234, a, w, "x") == two + EN.encode("  ")       # 4 short: spaces
    assert insert.fit(two, 10, 0x7F1234, a, w, "x") == two + insert.far(0x7F1234) + b"\0"  # jump over the rest
    long = EN.encode("abcdef")
    slot = insert.fit(long, 6, 0x048000, a, w, "x")
    (off, moved), = w.puts
    assert off == 0x308000  # did not cross the 32 KB bank at 0x308000
    assert moved == long + insert.far(0x048000)
    assert slot == insert.far(insert.cpu_of(0x308000)) + b"\0"
    assert insert.cpu_of(0x308000) == 0xE18000
    with pytest.raises(ValueError):
        insert.fit(long, 4, 0, a, w, "x")
