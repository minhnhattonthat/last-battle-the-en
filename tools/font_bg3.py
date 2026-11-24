"""English lowercase and punctuation for the 8x8 BG3 font (LZ block 319, `top2`, loaded at VRAM byte $C000).

The game's BG3 font has digits ($01-$0A) and capitals ($0B-$24) but no lowercase; the tiles after them are hiragana
($25-$5F), katakana and symbols. Byte names drawn through 01:FEAA (shop list, item lists, character names) and,
from phase 8, the BG3 menu labels are English, so the hiragana tiles from $25 on are redrawn with the glyphs below
(the Japanese menu labels that still use them garble until phase 8 translates them).

Style copied from the capitals and digits: bold (2 px vertical stems, 1 px horizontals), background colour 1, ink
colour 3, row 0 blank, capitals on rows 1-7. Lowercase: x-height rows 3-7; ascenders from row 1; letters with a
descender (g j p q y) have a 3-row body (rows 3-5) and the tail in rows 6-7, since the cell has no row below the
capitals' baseline. `#` = ink, `.` = background. (Thin 1 px lowercase until 2026-11-24: "No" next to a bold "OK".)
"""

BLOCK = 319           # LZ block index (blocks.unpack order)
FIRST = 0x25          # first tile redrawn

GLYPHS = {
    "a": ["........", "........", "........", ".####...", "....##..", ".#####..", "##..##..", ".#####.."],
    "b": ["........", "##......", "##......", "#####...", "##..##..", "##..##..", "##..##..", "#####..."],
    "c": ["........", "........", "........", ".####...", "##..##..", "##......", "##..##..", ".####..."],
    "d": ["........", "....##..", "....##..", ".#####..", "##..##..", "##..##..", "##..##..", ".#####.."],
    "e": ["........", "........", "........", ".####...", "##..##..", "######..", "##......", ".####..."],
    "f": ["........", "..###...", ".##.....", "####....", ".##.....", ".##.....", ".##.....", ".##....."],
    "g": ["........", "........", "........", ".#####..", "##..##..", ".#####..", "....##..", ".####..."],
    "h": ["........", "##......", "##......", "#####...", "##..##..", "##..##..", "##..##..", "##..##.."],
    "i": ["........", ".##.....", "........", "###.....", ".##.....", ".##.....", ".##.....", "####...."],
    "j": ["........", "...##...", "........", "..###...", "...##...", "...##...", "##.##...", ".###...."],
    "k": ["........", "##......", "##......", "##..##..", "##.##...", "####....", "##.##...", "##..##.."],
    "l": ["........", "###.....", ".##.....", ".##.....", ".##.....", ".##.....", ".##.....", "####...."],
    "m": ["........", "........", "........", "######..", "##.#.##.", "##.#.##.", "##.#.##.", "##.#.##."],
    "n": ["........", "........", "........", "#####...", "##..##..", "##..##..", "##..##..", "##..##.."],
    "o": ["........", "........", "........", ".####...", "##..##..", "##..##..", "##..##..", ".####..."],
    "p": ["........", "........", "........", "#####...", "##..##..", "#####...", "##......", "##......"],
    "q": ["........", "........", "........", ".#####..", "##..##..", ".#####..", "....##..", "....##.."],
    "r": ["........", "........", "........", "##.##...", "###..#..", "##......", "##......", "##......"],
    "s": ["........", "........", "........", ".#####..", "##......", ".####...", "....##..", "#####..."],
    "t": ["........", ".##.....", ".##.....", "#####...", ".##.....", ".##.....", ".##.....", "..###..."],
    "u": ["........", "........", "........", "##..##..", "##..##..", "##..##..", "##..##..", ".#####.."],
    "v": ["........", "........", "........", "##..##..", "##..##..", "##..##..", ".####...", "..##...."],
    "w": ["........", "........", "........", "##...##.", "##.#.##.", "##.#.##.", "##.#.##.", ".##.##.."],
    "x": ["........", "........", "........", "##..##..", ".####...", "..##....", ".####...", "##..##.."],
    "y": ["........", "........", "........", "##..##..", "##..##..", ".#####..", "....##..", ".####..."],
    "z": ["........", "........", "........", "######..", "...##...", "..##....", ".##.....", "######.."],
    "'": ["........", "##......", "##......", ".#......", "........", "........", "........", "........"],
    ",": ["........", "........", "........", "........", "........", "##......", "##......", ".#......"],
    ".": ["........", "........", "........", "........", "........", "........", "##......", "##......"],
    "-": ["........", "........", "........", "........", "#####...", "........", "........", "........"],
    "!": ["........", "##......", "##......", "##......", "##......", "##......", "........", "##......"],
    "?": ["........", ".####...", "##..##..", "...##...", "..##....", "..##....", "........", "..##...."],
    "&": ["........", ".###....", "##.##...", ".###....", "###..#..", "##.##...", "##..#...", ".###.##."],
    "/": ["........", ".....##.", "....##..", "....##..", "...##...", "..##....", "..##....", ".##....."],
    ":": ["........", "........", "##......", "##......", "........", "........", "##......", "##......"],
    "+": ["........", "........", "..##....", "..##....", "######..", "..##....", "..##....", "........"],
}
ORDER = "abcdefghijklmnopqrstuvwxyz',.-!?&/:+"
TILE = {c: FIRST + i for i, c in enumerate(ORDER)}


def tile_bytes(rows):
    """8 rows of `#`/`.` -> one 2bpp tile: background colour 1 (plane 0), ink colour 3 (both planes)."""
    assert len(rows) == 8 and all(len(r) == 8 for r in rows), rows
    out = bytearray()
    for r in rows:
        ink = int(r.replace("#", "1").replace(".", "0"), 2)
        out += bytes([0xFF, ink])
    return bytes(out)


BATTLE_FONT, BATTLE_LEN = 0x150000, 0xB34   # battle copy of this font, battle LZ ($2A:8000, tools/blz.py)
BATTLE_LEN_AT = [0x1404A4, 0x14736C]      # its compressed length in the two battle load lists (entry + 7)


def battle_patch(orig, writer):
    """The battle BG3 font (its own copy, battle LZ, loaded by 30:F410 to VRAM $6000) with the English tiles."""
    import blz
    d = blz.decode(orig[BATTLE_FONT:], BATTLE_LEN)
    enc = blz.encode(d[:2] + patch(d[2:]))
    assert len(enc) <= BATTLE_LEN, f"battle font {len(enc)} bytes > {BATTLE_LEN}"
    writer.put(BATTLE_FONT, enc, "battle font: English BG3 tiles")
    for at in BATTLE_LEN_AT:
        assert orig[at:at + 2] == BATTLE_LEN.to_bytes(2, "little"), f"battle load list moved ({at:X})"
        writer.put(at, len(enc).to_bytes(2, "little"), "battle font length")
    battle_names_patch(orig, writer, BATTLE_FONT + len(enc))


# Battle status-box party names (phase 8). The second battle stream (battle LZ, right after the font at $2A:8B34,
# to VRAM word $6C00, i.e. BG3 tile $180 + n) holds the name graphics: クルト = tiles $1A4-$1A6, メイ $1A7-$1A8,
# ボルグ = $1A9 $1A5 $1A4 (shares Kurt's kana), レジーナ $1AA-$1AD. The status-box tilemap is raw at file 0x1F084A
# (one 15-word row per member, 4 name words before the bar tile $39AE). English names are drawn in a compact
# 4 px font across their own tiles; Borg gets two new tiles after the stream's end ($1FB-$1FC, zero and unused in
# battle VRAM, work/qa/bw7/battle_field ppu dump). Rows 1-7 like the kana; ink colour 3 on colour 0 (transparent).
NAME_STREAM, NAME_LEN = 0x150B34, 0x509
COLUMN_AT = 0x150FF0   # $2A:8FF0 up to the old stream's end: spare (zeroed); column data is at battle_text.COLUMN_DATA
NAME_ENTRY = [0x1404A6, 0x14736E]          # load-list entries: +2 VRAM word, +4 24-bit source, +7 length
NAME_GLYPHS = {
    "K": ["....", "#..#", "#.#.", "##..", "##..", "#.#.", "#..#", "#..#"],
    "M": [".....", "#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "B": ["....", "###.", "#..#", "#..#", "###.", "#..#", "#..#", "###."],
    "R": ["....", "###.", "#..#", "#..#", "###.", "#.#.", "#..#", "#..#"],
    "u": ["....", "....", "....", "#..#", "#..#", "#..#", "#..#", ".###"],
    "r": ["...", "...", "...", "#.#", "##.", "#..", "#..", "#.."],
    "t": ["...", ".#.", ".#.", "###", ".#.", ".#.", ".#.", "..#"],
    "e": ["....", "....", "....", ".##.", "#..#", "####", "#...", ".###"],
    "i": ["#", "#", ".", "#", "#", "#", "#", "#"],
    "o": ["....", "....", "....", ".##.", "#..#", "#..#", "#..#", ".##."],
    "g": ["....", "....", "....", ".###", "#..#", ".###", "...#", ".##."],
    "n": ["....", "....", "....", "###.", "#..#", "#..#", "#..#", "#..#"],
    "a": ["....", "....", "....", ".##.", "...#", ".###", "#..#", ".###"],
}
NAME_ROWS = {  # file offset of the name's first tilemap word -> (English name, BG3 tiles it is drawn on)
    0x1F084A: ("Kurt", [0x1A4, 0x1A5, 0x1A6]),
    0x1F0868: ("Mei", [0x1A7, 0x1A8]),
    0x1F0886: ("Borg", [0x1A9, 0x1FB, 0x1FC]),
    0x1F08A4: ("Regina", [0x1AA, 0x1AB, 0x1AC, 0x1AD]),
}
NAME_ORIG_ROWS = {0x1F084A: [0x1A4, 0x1A5, 0x1A6], 0x1F0868: [0x1A7, 0x1A8], 0x1F0886: [0x1A9, 0x1A5, 0x1A4],
                  0x1F08A4: [0x1AA, 0x1AB, 0x1AC, 0x1AD]}


def name_tiles(name, ntiles):
    """English name -> ntiles 2bpp tiles: glyphs from x=1 with a 1 px gap, ink colour 3 on colour 0."""
    width = 8 * ntiles
    canvas = [[0] * width for _ in range(8)]
    x = 1
    for c in name:
        g = NAME_GLYPHS[c]
        w = len(g[0])
        assert x + w <= width, f"{name!r} is wider than {ntiles} tiles"
        for y, row in enumerate(g):
            for i, p in enumerate(row):
                if p == "#":
                    canvas[y][x + i] = 3
        x += w + 1
    out = []
    for t in range(ntiles):
        tb = bytearray()
        for y in range(8):
            px = canvas[y][t * 8:(t + 1) * 8]
            p0 = sum((v & 1) << (7 - i) for i, v in enumerate(px))
            p1 = sum((v >> 1) << (7 - i) for i, v in enumerate(px))
            tb += bytes([p0, p1])
        out.append(bytes(tb))
    return out


def battle_names_patch(orig, writer, start):
    """Redraw the battle status names (second battle stream), place the stream at `start` (right after the
    re-encoded font, same bank $2A) and point both load lists at it; rewrite the tilemap rows."""
    import blz
    raw = blz.decode(orig[NAME_STREAM:], NAME_LEN)
    size = int.from_bytes(raw[:2], "little")
    d = bytearray(raw[2:2 + size])
    top = max(t for _, tiles in NAME_ROWS.values() for t in tiles) - 0x180 + 1
    assert top <= 0x200 - 0x180, "name tiles past BG3 tile $1FF"
    d += bytes(max(0, top * 16 - len(d)))
    for name, tiles in NAME_ROWS.values():
        for t, tb in zip(tiles, name_tiles(name, len(tiles))):
            d[(t - 0x180) * 16:(t - 0x180 + 1) * 16] = tb
    enc = blz.encode(len(d).to_bytes(2, "little") + bytes(d))
    end = COLUMN_AT  # the rest of the old stream's space is cleared by battle_text.column_messages
    assert start + len(enc) <= end, f"battle name stream {len(enc)} bytes does not fit before {end:X}"
    assert (start & ~0x7FFF) == (end - 1 & ~0x7FFF), "stream must stay in bank $2A"
    writer.put(start, enc + b"\x00" * (end - start - len(enc)), "battle names: English status-box name tiles")
    src = (0x2A << 16) | 0x8000 | (start & 0x7FFF)
    for e in NAME_ENTRY:
        assert orig[e + 2:e + 4] == b"\x00\x6c" and orig[e + 4:e + 9] == bytes([0x34, 0x8B, 0x2A, 0x09, 0x05]), \
            f"battle name load entry moved ({e:X})"
        writer.put(e + 4, src.to_bytes(3, "little") + len(enc).to_bytes(2, "little"), "battle names: source, length")
    for at, (name, tiles) in NAME_ROWS.items():
        old = [int.from_bytes(orig[at + 2 * i:at + 2 * i + 2], "little") for i in range(len(tiles))]
        assert [w & 0x3FF for w in old] == NAME_ORIG_ROWS[at], f"battle name row moved ({at:X})"
        new = b"".join(((w & 0xFC00) | t).to_bytes(2, "little") for w, t in zip(old, tiles))
        if new != orig[at:at + len(new)]:
            writer.put(at, new, f"battle names: {name} tilemap row")


def patch(data):
    """Return block 319's data with the English tiles written in."""
    d = bytearray(data)
    for c in ORDER:
        t = TILE[c]
        assert (t + 1) * 16 <= len(d), c
        d[t * 16:(t + 1) * 16] = tile_bytes(GLYPHS[c])
    return bytes(d)
