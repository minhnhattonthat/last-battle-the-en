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


def test_bank_pool_repoints_short_slot():
    w, p = W(), insert.BankPools()
    data = EN.encode("Mei") + insert.far(0x04B2E6)
    orig = bytearray(0x40000)
    orig[0x232D4:0x232D6] = (0xB2E2).to_bytes(2, "little")  # the slot points at the string, as in the ROM
    p.repoint(0x232E2, data, {"id": "b04_B2E2", "size": 4, "ptrs": ["0232D4"]}, w, orig)
    p.repoint(0x232E2, data, {"id": "b04_B2E2", "size": 4, "ptrs": ["0232D4"]}, w, orig)
    assert w.puts == [(0x27F00, data), (0x232D4, b"\x00\xff"),
                      (0x27F00 + len(data), data), (0x232D4, (0xFF00 + len(data)).to_bytes(2, "little"))]
    with pytest.raises(ValueError):
        p.repoint(0x12345, data, {"id": "r", "size": 2, "ptrs": ["012340"]}, w, orig)
    with pytest.raises(AssertionError):  # a wrong slot id: its bytes are not the string's address
        p.repoint(0x232E2, data, {"id": "b04_B2E2", "size": 4, "ptrs": ["0232D6"]}, w, orig)


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
    # 9-letter field squeezes (D18) split inside the word, never cut at 8 ("AllElixi/r" in the battle item list)
    assert insert.battle_rows("AllElixir") == ("  All   ", " Elixir ")
    assert insert.battle_rows("Sil.Sword") == ("  Sil.  ", " Sword  ")
    assert insert.battle_rows("Longsword") == (" Long-  ", " sword  ")
    assert not insert.battle_fits("Abcdefghij")
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
def test_battle_text_rects():
    import json
    import battle_text
    import font_bg3
    orig = ORIG.read_bytes()
    es = {e["id"]: e for e in json.loads((ROOT / "script" / "battle.json").read_text(encoding="utf-8"))["entries"]}
    cmd = es["bt_1987A5"]                                      # command label たたかう: 4x2 rect read by a table script
    assert (cmd["w"], cmd["h"], cmd["geom"]) == (4, 2, "table") and cmd["jp"].endswith("たたかう")
    assert es["bt_186606"]["geom"] == "script"                 # まひが なおった, direct LDA #; JSL $29A1EA
    for e in es.values():                                      # markers keep the tile count; borders kept
        m = battle_text.encode(orig, {**e, "en": battle_text.marker_text(e)})
        assert len(m) == e["size"], e["id"]
    got = battle_text.encode(orig, {**cmd, "en": "{nl}Atk"})
    a = 0x2000
    assert got == b"".join(x.to_bytes(2, "little") for x in
                           [a | 0x93] * 4 + [a | 0x0B, a | font_bg3.TILE["t"], a | font_bg3.TILE["k"], a | 0x93])
    with pytest.raises(ValueError):
        battle_text.encode(orig, {**cmd, "en": "Fight!"})       # 6 tiles > 4
    with pytest.raises(ValueError):
        battle_text.encode(orig, {**cmd, "en": "A{nl}B{nl}C"})  # 3 rows > 2


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
    assert p[2:] == font_bg3.patch(d[2:])                    # every tile, not only the redrawn ones
    t = font_bg3.TILE["a"]
    assert p[2 + 16 * t:2 + 16 * (t + 1)] == font_bg3.tile_bytes(font_bg3.GLYPHS["a"])


def test_blz_copies_never_overlap_their_output():
    """The game's decoder reads a copy's whole source before writing it; an encoder copy with offset < length
    decoded into garbage tiles in battle (box borders, '!', digits: VRAM dump 2026-11-24). Fills cover runs."""
    import blz
    data = b"ab" * 40 + bytes(range(50)) + b"xyzxyzxyzq" * 5
    e = blz.encode(data)
    i = 0
    while i < len(e) - 1:
        c = e[i]
        if not c & 0x80:
            off, n = ((c << 8 | e[i + 1]) >> 4) & 0x7FF, (e[i + 1] & 15) + 2
            assert n <= off, (i, off, n)
            i += 2
        elif not c & 0x40:
            i += 1 + (c & 0x3F) + 1
        else:
            i += (2 if c & 0x20 else 1) + ((c >> 3) & 3) + 1
    assert blz.decode(e, len(e)) == data


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


def test_item_name_fields_fit_their_windows():
    """asm nm_icap: every return address follows a `JSR $F3C0` inside its FA op's handler, and with each list's
    name field (tiles; $8000 = the name takes the space before it) every row of every bank-04 window script using
    that op stays within the window's width (low byte of the header's second word)."""
    import re
    rom = bytearray(ORIG.read_bytes())
    for off, (old, new) in insert.WINDOW_HEADERS.items():  # the widths the build gives
        assert rom[off:off + 4] == old
        rom[off:off + 4] = new
    word = lambda o: int.from_bytes(rom[o:o + 2], "little")  # noqa: E731
    src = (ROOT / "asm" / "vwf.asm").read_text(encoding="utf-8")
    tab = re.findall(r"dw \$([0-9A-F]{4}), \$([0-9A-F]{4})\s+; (FA[0-9A-F]{2})", src)
    assert len(tab) == 6
    scripts = 0
    for ret, field, op in tab:
        ret, field, op = int(ret, 16), int(field, 16), int(op, 16)
        assert rom[ret - 2:ret + 1] == b"\x20\xc0\xf3"      # bank 01: file offset = CPU address
        handler = word(0xE679 + 2 * (op & 0xFF))
        assert handler < ret - 2 < handler + 0x50
        tiles = (field & 0xFF) - (1 if field & 0x8000 else 0)
        heads = set()
        for m in re.finditer(op.to_bytes(2, "little"), rom[0x20000:0x28000]):
            s = 0x20000 + m.start()
            while word(s - 2) != 0xFF00:
                s -= 2
            heads.add(s)
        assert heads
        for s in heads:
            width, o, row = word(s + 2) & 0xFF, s + 4, 0
            while True:
                w = word(o)
                o += 2
                if w in (0xFE00, 0xFF00):
                    assert row <= width, (hex(s), op)
                    row = 0
                    if w == 0xFF00:
                        break
                else:
                    row += tiles if w == op else 1
            scripts += 1
    assert scripts >= 8


@pytest.mark.skipif(not ORIG.exists(), reason="no ROM")
def test_english_build_moves(tmp_path):
    """Phase 7: the English build passes romdiff (build.build raises otherwise), the moved shop command window is
    reached through its window-table word and starts with the original header, every repointed 2-tile label's
    pointer lands on its English ending in `00 FF`, and the widened item windows have their new headers."""
    import json
    import build
    from textcodec import bg3_en
    rom, _ = build.build(tmp_path / "en.sfc")
    orig = ORIG.read_bytes()
    word = lambda b, o: int.from_bytes(b[o:o + 2], "little")  # noqa: E731
    for lo, hi, ptr in insert.MOVED_WINDOWS:
        at = 0x20000 + (word(rom, int(ptr, 16)) & 0x7FFF)
        assert at != lo and rom[at:at + 4] == orig[lo:lo + 4]
        assert at <= rom.find(b"\x00\xff", at) < at + (hi - lo) + 16
    menus = {e["id"]: e for e in json.loads((ROOT / "script" / "menus.json").read_text(encoding="utf-8"))["entries"]}
    for eid, ptrs in insert.BG3_PTRS.items():
        enc = bg3_en().encode(menus[eid]["en"])
        for p in ptrs:
            at = 0x20000 + (word(rom, int(p, 16)) & 0x7FFF)
            assert rom[at:at + len(enc) + 2] == enc + b"\x00\xff", eid
    for off, (_, new) in insert.WINDOW_HEADERS.items():
        assert rom[off:off + 4] == new
    import battle_text                                    # item found: the six stores spell FOUND_EN in order
    code = rom[battle_text.FOUND_AT:battle_text.FOUND_AT + 54]
    stored = [word(code, i + 1) for i in range(len(code) - 4) if code[i] == 0xA9 and code[i + 3:i + 5] == b"\x87\x50"]
    assert stored == battle_text.en_codec(orig, 0x2000).words(battle_text.FOUND_EN)
    # column-typed messages: every op copies the message so far from column 0 (w = columns reached, h = 2), and
    # the last one reads back as the English rows
    for at, _, top, bottom in battle_text.COLUMN_MSGS:
        ops = battle_text.column_ops(orig, at)
        v0, reach = word(orig, ops[0] + 1), 0
        for o in ops:
            reach = max(reach, (word(orig, o + 1) - v0) // 2 + 1)
            src = (rom[o + 5] & 0x7F) << 15 | word(rom, o + 3) & 0x7FFF
            assert battle_text.COLUMN_DATA <= src < battle_text.COLUMN_DATA + battle_text.COLUMN_LEN, hex(o)
            assert word(rom, o + 1) == v0 and rom[o + 6:o + 8] == bytes([reach, 2]), hex(o)
        attr = word(rom, src) & battle_text.ATTR_MASK
        c = battle_text.en_codec(orig, attr)
        for r, text in enumerate((top, bottom)):
            want = c.words(text) + [attr | battle_text.SPACE] * (reach - len(text))
            assert [word(rom, src + 2 * (r * reach + i)) for i in range(reach)] == want, text
    # strings.tsv (text coverage): one key per string; a block key names a stream of this build that decompresses
    # far enough to hold the string's slot, a ROM key lies in the ROM
    import lz
    import strings_tsv
    rows = [line.split("\t") for line in (tmp_path / "strings.tsv").read_text(encoding="utf-8").splitlines()
            if not line.startswith("#")]
    ids = {e["id"] for f in insert.load().values() for e in f["entries"]}
    assert sorted(r[0] for r in rows) == sorted(ids)
    streams = {}
    for _, k in rows:
        k = int(k, 16)
        if k & strings_tsv.BLOCK_KEY:
            off = k >> 16 & 0xFFFFFF
            if off not in streams:
                streams[off] = lz.decompress(rom, off)[0]
            assert k & 0xFFFF < len(streams[off]), hex(k)
        else:
            assert k < len(rom)


@pytest.mark.skipif(not ORIG.exists(), reason="no ROM")
def test_battle_vwf():
    """Battle VWF (tools/bvwf.py, asm bvwf_rect): the asm constants match bvwf.py, the canvas lies between the battle
    font and the status-name stream, every text tile has a glyph, the run model splits as specified, and no English
    run in script/battle.json is wider in proportional type than the cells it replaces."""
    import json
    import re
    import battle_text
    import blz
    import bvwf
    import font_bg3
    asm = (ROOT / "asm" / "vwf.asm").read_text(encoding="utf-8")
    assert int(re.search(r"!BV_BASE\s*=\s*\$([0-9A-F]+)", asm).group(1), 16) == bvwf.BASE
    assert int(re.search(r"!BV_N\s*=\s*(\d+)", asm).group(1)) == bvwf.COUNT
    assert re.search(r"!i < (\d+)", asm).group(1) == str(-(-bvwf.COUNT // bvwf.CHUNK))   # one descriptor per chunk
    orig = ORIG.read_bytes()
    font = blz.decode(orig[font_bg3.BATTLE_FONT:], font_bg3.BATTLE_LEN)
    assert int.from_bytes(font[:2], "little") // 16 <= bvwf.BASE        # the battle font ends before the canvas
    assert bvwf.BASE + bvwf.COUNT <= 0x180                               # the status-name stream starts at $180
    f, widths, chars = bvwf.tables(orig)
    texts = {c for c in chars if c}
    assert all(widths[c - 0x20] > 0 for c in texts) and max(widths) <= 9
    assert chars[bvwf.SPACE] == 0x20 and chars[0x0B] == ord("A") and chars[font_bg3.TILE["a"]] == ord("a")
    assert not any(chars[1 + i] for i in range(10))                      # digits stay fixed-width tiles
    cells = list("Def  +") + [None] + list(" Kurt ran")
    assert bvwf.runs(cells) == [(0, 2, "Def"), (5, 5, "+"), (8, 15, "Kurt ran")]
    doc = json.loads((ROOT / "script" / "battle.json").read_text(encoding="utf-8"))
    bad = []
    for e in doc["entries"]:
        if not e["en"]:
            continue
        ws = battle_text.encode(orig, e)
        ws = [int.from_bytes(ws[i:i + 2], "little") for i in range(0, len(ws), 2)]
        for r in range(e["h"]):
            row = [chr(chars[w & 0x3FF]) if (w & 0x3FF) < 0x100 and chars[w & 0x3FF] else None
                   for w in ws[r * e["w"]:(r + 1) * e["w"]]]
            bad += [(e["id"], o) for o in bvwf.overflow(widths, row)]
    assert not bad, bad
