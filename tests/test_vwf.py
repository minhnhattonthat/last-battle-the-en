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


def test_bg3_font_lowercase():
    import font_bg3
    assert set(font_bg3.ORDER) == set(font_bg3.GLYPHS) and len(font_bg3.ORDER) == len(set(font_bg3.ORDER))
    assert font_bg3.FIRST > 0x24                       # after the capitals Z = $24
    assert max(font_bg3.TILE.values()) < 0x60           # inside the hiragana run, before katakana
    tile = font_bg3.tile_bytes(font_bg3.GLYPHS["a"])
    assert tile[0::2] == b"\xff" * 8                    # plane 0 = background colour 1 everywhere
    assert all(font_bg3.GLYPHS[c][0] == "." * 8 for c in font_bg3.ORDER)   # row 0 blank, as the capitals


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


ORIG = ROOT / "rom" / "Last Battle, The (Japan).sfc"


@pytest.mark.skipif(not ORIG.exists(), reason="no ROM")
def test_name_escape_and_table():
    orig = ORIG.read_bytes()
    t = insert.NameTable(orig)
    assert t.add(1, 5, "Long Sword", "item_05") == b"\x01\x05"
    with pytest.raises(ValueError):
        t.add(1, 6, "ソード", "x")
    w = W()
    t.write(w)
    (off, blob), = w.puts
    assert off == insert.NAMES_AREA
    bg3 = [int.from_bytes(blob[2 * c:2 * c + 2], "little") for c in range(128)]
    assert bg3[ord("A")] == 0x0B and bg3[ord("0")] == 0x01  # the byte map's own tiles
    import font_bg3
    assert bg3[ord("a")] == font_bg3.TILE["a"] and bg3[ord("'")] == font_bg3.TILE["'"]  # English BG3 tiles
    ptr = lambda i: int.from_bytes(blob[0x100 + 2 * i:0x102 + 2 * i], "little") - 0x8000  # noqa: E731
    assert blob[ptr(5):ptr(5) + 11] == b"Long Sword\0"
    assert blob[ptr(7)] == 0  # unused -> empty name
    assert max(ptr(i) for i in range(512)) < len(blob)


def test_battle_rows():
    """Battle name windows: 8 tiles x 2 rows (asm/vwf.asm bt_name)."""
    assert insert.battle_rows("Kobold") == (" " * 8, " Kobold ")
    assert insert.battle_rows("Purple Slime") == (" Purple ", " Slime  ")
    assert insert.battle_rows("[enemy_07]The quick") == ("enemy_07", "The quic")
    assert insert.battle_fits("Thunder Dragon") and not insert.battle_fits("Will-o'-the-Wisp Lord")
    assert insert.battle_rows("Fire " + insert.RANK_MARK)[1].strip() == "Fire " + insert.RANK_MARK


@pytest.mark.skipif(not ORIG.exists(), reason="no ROM")
def test_battle_name_table_and_bytes():
    orig = ORIG.read_bytes()
    t = insert.NameTable(orig)
    t.add(3, 8, "Purple Slime", "enemy_07")
    w = W()
    t.write(w)
    (_, blob), = w.puts
    bt = 0x100 + 2 * 256 * insert.NAME_KINDS_MAX          # BT_PTRS ($FC9100 in asm/vwf.asm)
    assert bt == 0x1100
    p = int.from_bytes(blob[bt + 2 * (2 * 256 + 8):bt + 2 * (2 * 256 + 8) + 2], "little") - 0x8000
    assert blob[p:p + 16] == b" Purple  Slime  "
    assert blob[p + 16:p + 32] == "".join(insert.battle_rows("Purple Slime \x01")).encode()  # the rank form
    blank = int.from_bytes(blob[bt:bt + 2], "little") - 0x8000
    assert blob[blank:blank + 32] == b" " * 32
    w = W()
    insert.battle_bytes(w)
    got = dict(w.puts)
    import font_bg3
    hi = lambda b: got[insert.BT_HI + 2 * (b - 0x30)]  # noqa: E731
    assert hi(ord("a")) == bytes([0x93, font_bg3.TILE["a"]])     # top blank, bottom = the English tile
    assert got[insert.BT_LO + 4 * (0x2D - 0x28)] == b"\x93\x20" + (0x2000 | font_bg3.TILE["-"]).to_bytes(2, "little")


@pytest.mark.skipif(not ORIG.exists(), reason="no ROM")
def test_battle_lz_roundtrip_and_font():
    import blz
    import font_bg3
    orig = ORIG.read_bytes()
    d = blz.decode(orig[font_bg3.BATTLE_FONT:], font_bg3.BATTLE_LEN)
    assert d[0] | d[1] << 8 == len(d) - 2 == 0x11A0           # size word = the DMA length (30:F445)
    e = blz.encode(d)
    assert blz.decode(e, len(e)) == d and len(e) <= font_bg3.BATTLE_LEN
    w = W()
    font_bg3.battle_patch(orig, w)
    font = w.puts[0][1]
    p = blz.decode(font, len(font))
    t = font_bg3.TILE["a"]
    assert p[2 + 16 * t:2 + 16 * (t + 1)] == font_bg3.tile_bytes(font_bg3.GLYPHS["a"])


def test_ruler_text():
    """Ruler build lines: 6 px digits, decade digit every 10th, as wide as the JP segment + 36 px, tokens kept."""
    assert all(font_en.width(c) == 6 for c in insert.RULER)
    assert insert.RULER[9] == "1" and insert.RULER[19] == "2" and len(insert.RULER) == 40
    e = {"jp": "あいう{nl}かきくけこさしすせそたちつてとなにぬねの", "id": "x"}
    a, b = insert.ruler_text(e).split("{nl}")
    assert a == insert.RULER[:12] and b == insert.RULER
    assert insert.ruler_text({"jp": "{nl}", "id": "y"}).endswith("{nl}")


def test_name_entry_grid():
    """English name entry: every grid cell's byte shows its own character in both byte maps, the row count is
    patched in all five places, and every write stays in the name-entry ranges."""
    import font_bg3

    class W:
        def __init__(self):
            self.w = {}

        def put(self, off, data, what):
            self.w[off] = data

    w = W()
    insert.name_entry(w)
    word = lambda off: int.from_bytes(w.w[off], "little")  # noqa: E731
    cells = w.w[insert.NE_BYTES_OFF]
    rows = w.w[insert.NE_ROWS_OFF]
    for i, c in enumerate("".join(insert.NE_GRID)):
        b = cells[i]
        if c == "_":
            assert b == 0xFF
            continue
        assert word(insert.GLYPH_MAP_OFF + 2 * (b - 0x2C)) == 0x0800 + ord(c)
        tile = word(insert.BG3_MAP_OFF + 2 * (b - 0x2C))
        assert int.from_bytes(rows[12 * (i // 5) + 2 * (i % 5):][:2], "little") == tile
        if c.islower():
            assert tile == font_bg3.TILE[c] and b == ord(c)
    assert [w.w[o][0] for o, _ in insert.NE_ROW_COUNT] == [14, 14, 14, 15, 15]


def test_bg3_marker_keeps_tile_count():
    """BG3 marker text: same tiles per line and the same tokens, so no BG3 string moves or reflows."""
    from textcodec import TOKEN
    e = {"id": "bg3_8F1C", "jp": "    {FA0F}は アイテムを もっていません{009F}{nl}はい"}
    m = insert.bg3_marker_text(e)
    assert m.startswith("8F1C") and TOKEN.findall(m) == TOKEN.findall(e["jp"])
    assert [len(TOKEN.sub("", x)) for x in m.split("{nl}")] == [len(TOKEN.sub("", x)) for x in e["jp"].split("{nl}")]
    assert insert.bg3_marker_text({"id": "bg3_8600", "jp": "        どうしますか？"}).startswith("8600:")


@pytest.mark.skipif(not ORIG.exists(), reason="no ROM")
def test_spell_rank_records():
    """Spell names with a rank letter in character records (raw new-game record + party members in blocks): found
    by insert.spell_refs; the build writes `02 n RANK 0..` there and asm nm_fee3/nm_feaa print ` RANK`."""
    import json
    import blocks
    from textcodec import JP, ByteCodec
    orig = ORIG.read_bytes()
    spells = json.loads((ROOT / "script" / "spells.json").read_text(encoding="utf-8"))["entries"]
    refs = insert.spell_refs(orig, blocks.unpack(orig), ByteCodec(orig, JP), spells)
    assert refs[0] == (None, 0x1FE36, 1, 0x41)
    assert len(refs) == 11 and {r[0] for r in refs[1:]} == {14, 23, 36, 81}
