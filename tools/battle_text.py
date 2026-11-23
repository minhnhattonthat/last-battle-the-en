"""battle_text.py: battle tile-word text (BG3 tile words with attribute bits, `$20xx`/`$21xx`), extracted as in-place
rectangles (docs/re/battle.md §Battle messages).

Battle windows are drawn by the window-script interpreter 29:A1EA (script in bank $33, A = address):
  op 00        copy               dest(2, $7E) src(3) w(1) h(1)   -> w x h tile words, rows contiguous at src
  op 01..FC    wait op frames, then the same copy
  op FE        value ptr(2) (30:927A draws the number), then the same copy
  op FD        jump addr(2)       op FF  end
Strings are (a) "script": the ROM rectangles those copies read, from every script reached by `LDA #addr; JSL
$29A1EA`; (b) "table": rectangles of copy ops found anywhere in bank $33 that read a run of >= MIN_KANA kana tile
words (tools/re_battle_text.py), for scripts reached through tables; (c) "scan": runs no rectangle covers (one row,
geometry a guess: drawn by other code, e.g. the victory line and the bank-$2D mana screen).
Text is written back in place, same tile count: English is laid row by row into the rectangle (rows split by {nl};
a two-row rectangle is usually a dakuten row over a kana row, so English can use both).

    python -X utf8 tools/battle_text.py [--rects]     list the strings"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from textcodec import WordCodec, bg3_tiles  # noqa: E402

SCRIPT_BANK = 0x33
INTERP = bytes([0x22, 0xEA, 0xA1, 0x29])  # JSL $29A1EA
ATTR_MASK = 0xFC00
SPACE = 0x93
# battle font tiles that differ from LZ block 319 (window borders), never kana here
NOT_KANA = set(range(0xA8, 0xAF))
MIN_KANA = 3
# scanned runs that are data, not text (checked by eye): the battle name tile table (0x140C38-0x140CB7, 29:B2B6)
# and short odd-aligned matches inside code/graphics
EXCLUDE = [(0x140B80, 0x140CB8), (0x16FC00, 0x16FC08), (0x170100, 0x170108), (0x1743A6, 0x1743AE),
           (0x18475E, 0x184766), (0x199DAC, 0x199DB6),
           (0x1A8DA9, 0x1A8DAF), (0x1C868F, 0x1C8695), (0x1DCE00, 0x1DCE08), (0x1EC899, 0x1EC89F), (0x1EEA5E, 0x1EEA64)]
# Window-script rects in bank $3E (victory EX / mana / LEVEL UP windows) that the kana-run search misses: names of
# two kana (メイ) or broken by ー (レジーナ), and dakuten-only rows over names (blanked by an English row).
EXTRA_RECTS = [(0x1F0090, 12, 2), (0x1F00F0, 12, 2), (0x1F0258, 24, 2), (0x1F0318, 24, 2),
               (0x1F04E8, 16, 1), (0x1F0508, 16, 1), (0x1F0548, 16, 1), (0x1F0568, 16, 1), (0x1F05B8, 24, 1)]


def off(bank, a):
    return (bank << 15) | (a & 0x7FFF)


def u16(rom, o):
    return rom[o] | rom[o + 1] << 8


def script_starts(rom):
    """Window script addresses (bank $33) loaded by LDA #imm right before a JSL $29A1EA."""
    return sorted({u16(rom, m.start() - 2) for m in re.finditer(re.escape(INTERP), rom) if rom[m.start() - 3] == 0xA9})


def parse(rom, a):
    """Copy ops of the window script at $33:a: [(op addr, dest, 24-bit src, w, h)]."""
    ops, seen = [], set()
    while a >= 0x8000 and a not in seen and len(ops) < 256:
        seen.add(a)
        o = off(SCRIPT_BANK, a)
        op = rom[o]
        if op == 0xFF:
            break
        if op == 0xFD:
            a = u16(rom, o + 1)
            continue
        p = o + 1 + (2 if op == 0xFE else 0)
        src = rom[p + 4] << 16 | u16(rom, p + 2)
        ops.append((a, u16(rom, p), src, rom[p + 5], rom[p + 6]))
        a += p + 7 - o
    return ops


def kana_map(rom):
    return {t: c for t, c in bg3_tiles(rom).items() if t not in NOT_KANA and t != SPACE}


def is_kana(c):
    return "ぁ" <= c <= "ヶ" and c != "・"


def codec(rom, attr):
    m = {attr | t: c for t, c in kana_map(rom).items()}
    m[attr | SPACE] = " "
    return WordCodec(m)


def words(rom, o, n):
    return [u16(rom, o + 2 * i) for i in range(n)]


def rects(rom):
    """{(file offset, w, h)} of every ROM source read by a directly reached window script with >= 1 kana tile."""
    km = kana_map(rom)
    out = set()
    for s in script_starts(rom):
        for _, _, src, w, h in parse(rom, s):
            bank = src >> 16
            if bank < 0x80 and bank >= 0x7E or bank == 0 or w == 0 or h == 0:
                continue
            o = off(bank & 0x7F, src & 0xFFFF)
            ws = words(rom, o, w * h)
            if any(is_kana(km.get(x & 0x3FF, "")) for x in ws):
                out.add((o, w, h))
    keep = set()
    for r in out:  # drop a rectangle inside another
        o, w, h = r
        if not any(q != r and q[0] <= o and o + 2 * w * h <= q[0] + 2 * q[1] * q[2] and q[1] == w for q in out):
            keep.add(r)
    return sorted(keep)


def table_rects(rom, runs):
    """Copy params (src24, w, h) of window-script ops in bank $33 that are reached through tables (not found by
    script_starts) and read one of runs [(start, size)]: any 5 bytes in bank $33 after an op byte <= $FC and a dest
    word whose rectangle overlaps a run at the same word alignment."""
    out = set()
    lo = SCRIPT_BANK << 15
    for i in range(lo + 3, lo + 0x8000 - 5):
        b, a, w, h = rom[i + 2], u16(rom, i), rom[i + 3], rom[i + 4]
        if not (0x28 <= b <= 0x3F and a >= 0x8000 and 1 <= w <= 32 and 1 <= h <= 28 and rom[i - 3] <= 0xFC):
            continue
        o = off(b, a)
        for st, n in runs:
            if o < st + n and o + 2 * w * h > st and (o - st) % 2 == 0:
                out.add((o, w, h))
    return out


def entries(rom):
    import re_battle_text
    km = kana_map(rom)
    runs = []
    for st, n, _ in re_battle_text.runs(rom):
        if any(a <= st < b for a, b in EXCLUDE):
            continue
        if sum(is_kana(km.get(x & 0x3FF, "")) for x in words(rom, st, n)) >= MIN_KANA:
            runs.append((st, 2 * n))
    rs = rects(rom)
    found = [(o, w, h, "script") for o, w, h in rs]
    tr = sorted(r for r in table_rects(rom, runs) - set(rs)
                if any(is_kana(km.get(x & 0x3FF, "")) for x in words(rom, r[0], r[1] * r[2])))
    found += [(o, w, h, "table") for o, w, h in tr
              if not any(q != (o, w, h) and q[0] <= o and o + 2 * w * h <= q[0] + 2 * q[1] * q[2] for q in rs + tr)]
    cov = set()
    for o, w, h, _ in found:
        cov.update(range(o, o + 2 * w * h))
    for o, w, h in EXTRA_RECTS:
        assert not any(k in cov for k in range(o, o + 2 * w * h)), f"extra rect {o:X} overlaps a found one"
        found.append((o, w, h, "extra"))
        cov.update(range(o, o + 2 * w * h))
    for st, n in runs:
        if not any(st + k in cov for k in range(n)):
            found.append((st, n // 2, 1, "scan"))
    out = []
    for o, w, h, geom in sorted(found):
        ws = words(rom, o, w * h)
        attrs = [x & ATTR_MASK for x in ws if is_kana(km.get(x & 0x3FF, ""))]
        attr = max(set(attrs), key=attrs.count) if attrs else 0x2000
        c = codec(rom, attr)
        rows = [c.decode(rom[o + 2 * w * r:o + 2 * w * (r + 1)]) for r in range(h)]
        out.append({"id": f"bt_{o:06X}", "file": f"{o:06X}", "size": 2 * w * h, "w": w, "h": h,
                    "attr": f"{attr:04X}", "geom": geom, "jp": "{nl}".join(rows), "en": ""})
    return out


def en_codec(rom, attr):
    """English: digits, capitals and the font_bg3 lowercase/punctuation tiles with the string's attribute bits;
    Japanese characters (fullwidth ＨＰ, kana kept on purpose) still encode to their original tiles."""
    from textcodec import bg3_en
    jp = codec(rom, attr)
    c = WordCodec({**jp.dec, **{attr | w: ch for w, ch in bg3_en().dec.items()}})
    for ch, w in jp.enc.items():  # fullwidth ＨＰ etc. share a word with ASCII H: keep the JP spelling encodable
        c.enc.setdefault(ch, w)
    return c


def encode(rom, e):
    """Bytes for e: the original tiles when e["en"] is empty, else English laid into the rectangle: rows split by
    {nl}, each padded with spaces to w, missing rows blank. Raises if a row is wider than w or rows > h."""
    attr = int(e["attr"], 16)
    if not e["en"]:
        return codec(rom, attr).encode(e["jp"].replace("{nl}", ""))
    c = en_codec(rom, attr)
    rows = e["en"].split("{nl}")
    if len(rows) > e["h"]:
        raise ValueError(f"{e['id']}: {len(rows)} rows > {e['h']}")
    out = b""
    for r in rows + [""] * (e["h"] - len(rows)):
        ws = c.words(r)
        if len(ws) > e["w"]:
            raise ValueError(f"{e['id']}: row {r!r} is {len(ws)} tiles > {e['w']}")
        ws += [attr | SPACE] * (e["w"] - len(ws))
        out += b"".join(x.to_bytes(2, "little") for x in ws)
    return out


# Battle-start messages typed one 1x2 column per frame: 8 copy ops (8 bytes each: op, dest(2), src(3), w=1, h=2)
# whose sources are kanji columns shared between the two messages (and the particles bt_198045 の, bt_1980E3 に).
# English columns go to font_bg3.COLUMN_AT and each op is repointed there; the old columns stay unused.
COLUMN_MSGS = [  # (script file offset, JP, top row, bottom row), each row <= 8 tiles
    (0x198000, "敵の奇襲攻撃!!", "Enemy", "ambush!!"),
    (0x1980A2, "奇襲攻撃に成功!", "Surprise", "attack!"),
]


def column_messages(orig, writer):
    import font_bg3
    cols, data = {}, bytearray()
    for at, _, top, bottom in COLUMN_MSGS:
        ops = [at + 8 * i for i in range(8)]
        assert all(orig[o + 5] == SCRIPT_BANK and orig[o + 6:o + 8] == b"\x01\x02" for o in ops), f"script moved {at:X}"
        attr = u16(orig, off(SCRIPT_BANK, u16(orig, ops[0] + 3))) & ATTR_MASK
        c = en_codec(orig, attr)
        t, b = c.words(top), c.words(bottom)
        assert len(t) <= 8 and len(b) <= 8, (top, bottom)
        t += [attr | SPACE] * (8 - len(t))
        b += [attr | SPACE] * (8 - len(b))
        for o, pair in zip(ops, zip(t, b)):
            if pair not in cols:
                cols[pair] = font_bg3.COLUMN_AT + len(data)
                data += b"".join(w.to_bytes(2, "little") for w in pair)
            f = cols[pair]
            writer.put(o + 3, ((f // 0x8000) << 16 | 0x8000 | f & 0x7FFF).to_bytes(3, "little"),
                       f"battle column message {at:X}")
    end = font_bg3.NAME_STREAM + font_bg3.NAME_LEN
    assert font_bg3.COLUMN_AT + len(data) <= end, f"column messages {len(data)} bytes"
    writer.put(font_bg3.COLUMN_AT, bytes(data) + bytes(end - font_bg3.COLUMN_AT - len(data)),
               "battle column messages: English columns")


def marker_text(e):
    """Marker build: every row holding kana becomes the offset (the id without `bt_`) and filler, same tile count,
    tokens (borders, dakuten, kanji pieces) kept; other rows stay as they are."""
    from insert import bg3_marker_text
    from textcodec import TOKEN
    tag = e["id"].split("_", 1)[1]
    return "{nl}".join(bg3_marker_text({"id": "x_" + tag, "jp": r}) if any(map(is_kana, TOKEN.sub("", r))) else r
                       for r in e["jp"].split("{nl}"))


def main():
    rom = (ROOT / "rom" / "Last Battle, The (Japan).sfc").read_bytes()
    es = entries(rom)
    for e in es:
        print(f"{e['id']} {e['w']:2d}x{e['h']:<2d} {e['geom']:6s} {e['jp']}")
    from collections import Counter
    print(len(es), "strings, geometry:", dict(Counter(e["geom"] for e in es)))


if __name__ == "__main__":
    main()
