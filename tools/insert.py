"""insert.py: write script/*.json back into the ROM image during build.py (docs/re/text.md).

Each entry's text is `en` when set, else `jp`, encoded and spliced back at its address: script blocks into the
block's decompressed data (blocks.Region repacks and recompresses only changed blocks), raw banks and byte names
through Writer.put. With no English every write reproduces the original bytes (tests/test_identity.py).

A string never changes size in place (block images and bank 04 keep every address, so no pointer moves): a longer one
is written to TEXT_AREA and its slot becomes a far jump there, the moved copy ending in a far jump back to the byte
after the slot; a shorter one is padded with spaces or followed by a far jump over the rest (docs/re/vwf.md §Far)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from textcodec import EN, JP, ByteCodec  # noqa: E402

SCRIPT = ROOT / "script"


def load(script_dir=SCRIPT):
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(script_dir).glob("*.json"))}


def override(files, qa):
    """QA builds: set `en` of the given ids (build.py --qa ID=TEXT). Unknown ids are an error."""
    left = dict(qa)
    for doc in files.values():
        for e in doc["entries"]:
            if e["id"] in left:
                e["en"] = left.pop(e["id"])
    if left:
        raise SystemExit(f"--qa: unknown ids {sorted(left)}")


FILLER = "The quick brown fox jumps over the lazy dog while five wizards vex a jolly king. "


def marker_text(e, jp_px=12):
    """Marker build: `[id]` then filler as wide (VWF px) as each Japanese line (12 px a glyph); control and insert
    tokens stay where they were, so paging, waits and names behave as in the original."""
    import font_en
    from textcodec import TOKEN
    out, first, pos = [], True, 0
    i, text = 0, e["jp"]
    while i <= len(text):
        m = TOKEN.search(text, i)
        seg = text[i:m.start() if m else len(text)]
        if seg:
            budget = len(seg) * jp_px
            s = f"[{e['id']}]" if first else ""
            first = False
            while True:
                c = FILLER[pos % len(FILLER)]
                if font_en.width(s + c) > budget and len(s) > 0:
                    break
                s += c
                pos += 1
            out.append(s)
        if not m:
            break
        out.append(m.group(0))
        i = m.end()
    if first:  # no text at all (only tokens): still show the id
        out.insert(0, f"[{e['id']}]")
    return "".join(out)


RULER = "".join("123456789" + str(d % 10) for d in range(1, 5))  # 40 digits, 6 px each: char k ends at 6k px


def ruler_text(e, n=len(RULER)):
    """Ruler build: every text segment of the Japanese line becomes RULER digits (6 px each; the 10th, 20th... digit
    is the decade, so the last digit seen in a shot gives the box width in px), as wide as the Japanese segment
    + 36 px (at most n digits; all of them would overflow the text area); tokens stay."""
    from textcodec import TOKEN
    out, i, text, seen = [], 0, e["jp"], False
    while i <= len(text):
        m = TOKEN.search(text, i)
        seg = text[i:m.start() if m else len(text)]
        if seg:
            out.append(RULER[:min(n, 2 * len(seg) + 6)])
            seen = True
        if not m:
            break
        out.append(m.group(0))
        i = m.end()
    if not seen:
        out.insert(0, RULER[:n])
    return "".join(out)


def bg3_marker_text(e):
    """Marker build, BG3 tile strings (fixed 8 px tiles): every line keeps its tile count and tokens, so nothing moves;
    the first line shows `addr:` (the id without `bg3_`), or as much of addr as fits, then filler."""
    from textcodec import TOKEN
    tag, out, first, pos = e["id"].split("_", 1)[1], [], True, 0
    i, text = 0, e["jp"]
    while i <= len(text):
        m = TOKEN.search(text, i)
        seg = text[i:m.start() if m else len(text)]
        if seg:
            n = len(seg)
            s = ""
            if first:
                s = f"{tag}:" if n >= len(tag) + 1 else tag[-n:]  # the BG3 font has no brackets
                first = False
            while len(s) < n:
                c = FILLER[pos % len(FILLER)]
                s += c if c != " " or len(s) + 1 < n else "x"
                pos += 1
            out.append(s[:n])
        if not m:
            break
        out.append(m[0])
        if m[0] == "{nl}":
            pos = 0
        i = m.end()
    return "".join(out)


def mark(files, fn=marker_text):
    """Marker build: every script string and byte name gets marker_text (ruler build: ruler_text); BG3 tile strings
    get bg3_marker_text in the marker build and stay Japanese in the ruler build (their width is their tile count)."""
    import battle_text
    for doc in files.values():
        if doc["source"]["kind"] == "battle":
            for e in doc["entries"]:
                e["en"] = battle_text.marker_text(e) if fn is marker_text else ""
            continue
        if doc["source"]["kind"] == "bg3":
            for e in doc["entries"]:
                e["en"] = bg3_marker_text(e) if fn is marker_text else ""
            continue
        if doc["source"]["kind"] == "names":
            for e in doc["entries"]:
                e["en"] = fn(e)
            continue
        for e in doc["entries"]:  # a slot too short for a far jump gets as much of its id as fits
            pooled = e.get("ptrs") and (int(e["file"], 16) & ~0x7FFF) in BANK_POOLS
            e["en"] = fn(e) if e["size"] >= FAR_LEN or pooled else e["id"][-(e["size"] // 2):]


def text_of(e):
    return e["en"] or e["jp"]


FAR = 0xF700     # far jump: word $F700 + 24-bit CPU address (asm/vwf.asm vm_dispatch, menu_fetch)
FAR_LEN = 5
TEXT_AREA = (0x300000, 0x3E0000)  # moved strings (4 MB build); blocks.EXPANSION stops below it
PAD_MAX = 4      # a string shorter than its slot by fewer than FAR_LEN + 1 bytes is padded with spaces


def far(cpu):
    return FAR.to_bytes(2, "little") + cpu.to_bytes(3, "little")


def cpu_of(off):
    """LoROM CPU address ($80+ mirror) of a file offset."""
    return ((off >> 15) | 0x80) << 16 | (off & 0x7FFF) | 0x8000


class TextAlloc:
    """Bump allocator in TEXT_AREA; a string never crosses a 32 KB bank (the VM steps a 16-bit pointer)."""

    def __init__(self, area=TEXT_AREA):
        self.pos, self.end = area

    def take(self, n):
        if (self.pos & 0x7FFF) + n > 0x8000:
            self.pos = (self.pos | 0x7FFF) + 1
        if self.pos + n > self.end:
            raise ValueError("text area full")
        off, self.pos = self.pos, self.pos + n
        return off


def fit(enc, size, ret, alloc, writer, eid, space=None):
    """The bytes for a size-byte slot holding enc; ret = CPU address of the byte after the slot; space = the pad word
    (default the VWF space)."""
    diff = size - len(enc)
    if diff == 0:
        return enc
    if 0 < diff <= PAD_MAX:
        return enc + (space or EN.encode(" ")) * (diff // 2)
    if diff > PAD_MAX:
        return (enc + far(ret)).ljust(size, b"\0")
    if size < FAR_LEN:
        raise ValueError(f"{eid}: {len(enc)} bytes for a {size}-byte slot, too short for a far jump")
    if alloc is None:
        raise ValueError(f"{eid}: {len(enc)} bytes for a {size}-byte slot (relocation needs the 4 MB build)")
    off = alloc.take(len(enc) + FAR_LEN)
    writer.put(off, enc + far(ret), f"moved:{eid}")
    return far(cpu_of(off)).ljust(size, b"\0")


# Bank-local pools for strings too short for a far jump but reached by 16-bit pointers (b04_B2E2): the string moves
# here (ending in a far jump back to the byte after its slot) and its pointers are rewritten. Bank 04's pool is the
# tail of the $FF padding at 0x27BE9-0x27FFF (docs/re/compression.md free-space candidates).
BANK_POOLS = {0x20000: (0x27F00, 0x28000)}


class BankPools:
    def __init__(self):
        self.pos = {base: lo for base, (lo, _) in BANK_POOLS.items()}

    def place(self, base, data, by, writer):
        """Write data into the pool of the bank at file offset base; returns its file offset."""
        at = self.pos[base]
        if at + len(data) > BANK_POOLS[base][1]:
            raise ValueError(f"{by}: bank pool at {base:06X} full")
        self.pos[base] = at + len(data)
        writer.put(at, data, f"pool:{by}")
        return at

    def repoint(self, off, data, e, writer, orig):
        base = off & ~0x7FFF
        if base not in BANK_POOLS:
            raise ValueError(f"{e['id']}: {len(data)} bytes for a {e['size']}-byte slot and no pool in its bank")
        for p in e["ptrs"]:  # a wrong slot id would pass romdiff (the log's expected bytes come from that slot)
            p = int(p, 16)
            assert p & ~0x7FFF == base, f"{e['id']}: pointer {p:06X} outside the string's bank"
            was = int.from_bytes(orig[p:p + 2], "little")
            assert was == (off & 0x7FFF) | 0x8000, f"{e['id']}: pointer {p:06X} holds ${was:04X}, not the string"
        at = self.place(base, data, e["id"], writer)
        for p in e["ptrs"]:
            p = int(p, 16)
            writer.put(p, ((at & 0x7FFF) | 0x8000).to_bytes(2, "little"), f"ptr:{e['id']}")


# BG3 strings in slots under FAR_LEN bytes but reached by a 16-bit pointer (D11 -> D18): with English longer than the
# slot they move whole, terminator included, to the bank pool and these pointers are rewritten. Item note table
# `$04:A2xx` (id, ptr) triples; equip-slot label table `$04:A71F`.
BG3_PTRS = {"bg3_A687": ["0222FF"], "bg3_A729": ["02271F"], "bg3_A737": ["022723"], "bg3_A73D": ["022725"]}
# Window scripts the build moves whole (header `xx yy ww hh`, then the script to `00 FF`) because a string inside
# them has a slot too short for a far jump: the shop command window (Buy / Sell / Info, 2-tile slots), reached
# through the window table word at 0x202EE.
MOVED_WINDOWS = [(0x21EE8, 0x21F0A, "0202EE")]
# Window headers the build changes (docs/re/windows.md, D18): the two field item windows of op FA0E (2 columns of
# space + name) move to x=0 and widen by 2 tiles, so each name gets 9 tiles (asm nm_icap), the most that fits left of
# the portrait window at x=22.
WINDOW_HEADERS = {0x2131A: (bytes.fromhex("010a120f"), bytes.fromhex("000a140f")),
                  0x21F7A: (bytes.fromhex("0101130f"), bytes.fromhex("0001150f")),
                  # item-name label beside the menu icons (FA18, 2 rows: dakuten + name): 8 -> 9 tiles so a 9-letter
                  # name isn't under the right border (stress_equip "Longsword"); x=14 after 3 icons, x=18 after 4
                  0x21656: (bytes.fromhex("0e020802"), bytes.fromhex("0e020902")),
                  0x21660: (bytes.fromhex("12020802"), bytes.fromhex("12020902"))}


def window_headers(orig, writer):
    for off, (old, new) in WINDOW_HEADERS.items():
        assert orig[off:off + 4] == old, f"window header {off:06X}"
        writer.put(off, new, f"window:{off:06X}")


NAMES_AREA = 0x3E0000   # $FC:8000: ASCII -> BG3 tile table, name pointers, English names (asm/vwf.asm nm_*)
NAME_KIND = {"items": 1, "spells": 2, "enemies": 3, "tactics": 4}  # escape in a record's name field: kind, n (1-255)
NAME_KINDS_MAX = 8        # pointer tables are sized for this many kinds (fixed addresses in asm/vwf.asm)
BT_W = 8                  # battle name windows: 8 tiles, two rows (29:B2B6; the top row is the dakuten row)
BG3_MAP_OFF = 0x22EAB     # byte -> BG3 tile word map of 01:FEAA (bytes $2C+)


def bg3_table(orig):
    """128 words: ASCII -> BG3 tile word. Digits and capitals are their own bytes in the name encoding; lowercase
    and the punctuation in `font_bg3` get the English tiles build.py draws over the hiragana; other characters
    their full-width form, else a space."""
    import struct
    import font_bg3
    bmap = struct.unpack_from("<212H", orig, BG3_MAP_OFF)
    bg_word = bmap[ord("A") - 0x2C] & 0xFC00   # attribute bits of a capital's tile word
    gmap = struct.unpack_from("<212H", orig, 0x23053)
    by_glyph = {}
    for i, w in enumerate(gmap):
        by_glyph.setdefault(w, i)
    out = []
    for c in range(128):
        if chr(c) in font_bg3.TILE:
            out.append(bg_word | font_bg3.TILE[chr(c)])
            continue
        ch = chr(c).upper()
        i = None
        if ch.isascii() and ch.isalnum():
            i = ord(ch) - 0x2C
        elif 0x21 <= c < 0x7F:
            try:
                w = int.from_bytes(JP.encode(chr(c + 0xFEE0))[:2], "little")
                i = by_glyph.get(w)
            except (KeyError, ValueError):
                i = None
        out.append(bmap[i] if i is not None else bmap[by_glyph[0x0300]])
    return struct.pack("<128H", *out)


RANK_MARK = "\x01"        # in a battle form: the record's rank capital goes here (asm/vwf.asm bt_tile)


def battle_rows(text, w=BT_W):
    """(top, bottom) rows of a battle name window, each w chars: a name that fits sits centred on the bottom row,
    a longer one is split at a space (or after a marker's `[id]`) into two centred rows; with no such split it is
    cut at w (battle_fits() says whether it fits)."""
    def centre(s):
        return (" " * ((w - len(s)) // 2) + s).ljust(w)

    if len(text) <= w:
        return " " * w, centre(text)
    if text.startswith("[") and "]" in text:  # marker: the id on top
        i = text.index("]")
        return centre(text[1:i][:w]), centre(text[i + 1:].strip()[:w])
    best = None
    for i, c in enumerate(text):
        if c == " " and i <= w and len(text) - i - 1 <= w:
            if best is None or max(i, len(text) - i - 1) < max(best, len(text) - best - 1):
                best = i
    if best is None:
        return text[:w], text[w:2 * w].ljust(w)
    return centre(text[:best]), centre(text[best + 1:])


def battle_fits(text, w=BT_W):
    top, bottom = battle_rows(text, w)
    return (top + bottom).replace(" ", "") == text.replace(" ", "")


class NameTable:
    """English byte names (4 MB build): escape bytes for the record, ASCII in NAMES_AREA.
    Layout ($FC:8000): NM_BG3 (128 words ASCII -> BG3 tile), NM_PTRS (256 words per kind, NAME_KINDS_MAX kinds),
    BT_PTRS (the same, to each name's battle form: rows top + bottom without rank, then top + bottom of
    name + " " + RANK_MARK, BT_W bytes each), then the data."""

    def __init__(self, orig):
        self.orig = orig
        self.ptrs = {}
        self.bt = {}
        self.data = bytearray(b"\0")  # offset 0 = the empty name every unused pointer gets
        self.data += b" " * (4 * BT_W)  # offset 1 = the blank battle form

    def add(self, kind, n, text, eid):
        if not text.isascii() or any(not 0x20 <= ord(c) < 0x7F for c in text):
            raise ValueError(f"{eid}: byte names take printable ASCII only")
        self.ptrs[(kind - 1) * 256 + n] = len(self.data)
        self.data += text.encode("ascii") + b"\0"
        self.bt[(kind - 1) * 256 + n] = len(self.data)
        for t in (text, text + " " + RANK_MARK):
            self.data += "".join(battle_rows(t)).encode("ascii")
        return bytes([kind, n])

    def write(self, writer):
        assert len(NAME_KIND) <= NAME_KINDS_MAX
        n = 256 * NAME_KINDS_MAX
        base = 0x8000 + 0x100 + 2 * 2 * n
        ptrs = bytearray()
        for i in range(n):
            ptrs += (base + self.ptrs.get(i, 0)).to_bytes(2, "little")
        for i in range(n):
            ptrs += (base + self.bt.get(i, 1)).to_bytes(2, "little")
        blob = bg3_table(self.orig) + ptrs + self.data
        assert len(blob) <= 0x8000, "name table past bank $FC"
        writer.put(NAMES_AREA, blob, "names:en")


# Name entry (docs/re/vwf.md §Name entry): the grid shows BG3 tile rows (12 bytes: 5 tile words + FF00, `$04:ACA7`,
# 01:FABC) and a cell gives byte `$04:B1FB + row * 5 + col` (01:ADF2); a name byte b >= $2C shows as glyph word
# `$04:B053[b - $2C]` (01:FEE3, dialogue) or BG3 tile `$04:AEAB[b - $2C]` (01:FEAA, load screen). English: the
# bytes are ASCII (digits, capitals, lowercase, and the punctuation below on free low bytes), both maps send them to
# the English glyph word / BG3 tile, and the grid has NE_ROWS rows instead of 43.
NE_ROWS_OFF, NE_BYTES_OFF, GLYPH_MAP_OFF = 0x22CA7, 0x231FB, 0x23053
EN_BASE_WORD = 0x0800  # textcodec.EN_BASE
NE_PUNCT = {0x2C: ",", 0x2D: "-", 0x2E: ".", 0x2F: "/", 0x3A: ":", 0x3B: "'", 0x3C: " ", 0x3D: "&", 0x3E: "!",
            0x3F: "?", 0x40: "+"}
NE_GRID = ["ABCDE", "FGHIJ", "KLMNO", "PQRST", "UVWXY", "Z.,'-", "abcde", "fghij", "klmno", "pqrst", "uvwxy",
           "z!?&/", "01234", "56789", ": +__"]  # "_" = empty cell (byte FF), " " = the space key
# operand bytes of LDA #$002A at 01:AE5D/FAC4/FACA and CMP #$002B at 01:AE6F/FB03 (file offset = bank-01 address)
NE_ROW_COUNT = [(0xAE5E, -1), (0xFAC5, -1), (0xFACB, -1), (0xAE70, 0), (0xFB04, 0)]


def name_entry(writer):
    """English name entry: byte maps for ASCII name bytes, the grid rows and cell bytes, the row count."""
    import font_bg3
    byte_of = {chr(b): b for b in list(range(0x30, 0x3A)) + list(range(0x41, 0x5B)) + list(range(0x61, 0x7B))}
    byte_of.update({c: b for b, c in NE_PUNCT.items()})

    def tile(c):
        if c == " ":
            return 0x93
        if c.isdigit():
            return 1 + int(c)
        if "A" <= c <= "Z":
            return 0x0B + ord(c) - 0x41
        return font_bg3.TILE[c]

    for c, b in sorted(byte_of.items(), key=lambda t: t[1]):
        writer.put(GLYPH_MAP_OFF + 2 * (b - 0x2C), (EN_BASE_WORD + ord(c)).to_bytes(2, "little"), f"ne:glyph {c!r}")
        writer.put(BG3_MAP_OFF + 2 * (b - 0x2C), tile(c).to_bytes(2, "little"), f"ne:bg3 {c!r}")
    rows, cells = bytearray(), bytearray()
    for r in NE_GRID:
        assert len(r) == 5, r
        for c in r:
            rows += tile(" " if c == "_" else c).to_bytes(2, "little")
        rows += b"\x00\xff"
        cells += bytes(0xFF if c == "_" else byte_of[c] for c in r)
    writer.put(NE_ROWS_OFF, bytes(rows), "ne:grid rows")
    writer.put(NE_BYTES_OFF, bytes(cells), "ne:grid bytes")
    for off, d in NE_ROW_COUNT:
        writer.put(off, bytes([len(NE_GRID) + d]), "ne:row count")


# Battle names (docs/re/battle.md): 29:B2B6 maps a name byte b to a (top, bottom) BG3 tile pair, b < $30 from 4-byte
# entries at BT_LO ($28:8C38 + 4 * (b - $28)), else 2 tile bytes at BT_HI ($28:8C58 + 2 * (b - $30), palette $2000).
# English party names are ASCII bytes (name entry): lowercase and NE_PUNCT get the English BG3 tiles.
BT_LO, BT_HI = 0x140C38, 0x140C58
BT_SPELLS, BT_SPELL_N = 0x19D3F1, 22   # default battle spell names, FF-centred 8-byte slots ($30:ACD5)


def battle_bytes(writer):
    import font_bg3
    for b in list(range(0x61, 0x7B)) + sorted(NE_PUNCT):
        c = chr(b) if b >= 0x61 else NE_PUNCT[b]
        t = 0x93 if c == " " else font_bg3.TILE[c]
        if b < 0x30:
            writer.put(BT_LO + 4 * (b - 0x28), (0x2093).to_bytes(2, "little") + (0x2000 | t).to_bytes(2, "little"),
                       f"bt:byte {c!r}")
        else:
            writer.put(BT_HI + 2 * (b - 0x30), bytes([0x93, t]), f"bt:byte {c!r}")  # top blank, bottom tile


def battle_spells(orig, writer, bc, spells):
    """Default battle spell names: a slot whose name is an English spell becomes that spell's escape."""
    if not any(e["en"] for e in spells):
        return
    by_name = {}
    for n, e in enumerate(spells, 1):
        by_name.setdefault(e["jp"], n)
    for i in range(BT_SPELL_N):
        off = BT_SPELLS + 8 * i
        jp = bc.decode(orig[off:off + 8].strip(b"\xff"))
        n = by_name.get(jp)
        assert n, f"battle spell slot {i} ({jp}) has no spells.json entry"
        if spells[n - 1]["en"]:
            writer.put(off, bytes([NAME_KIND["spells"], n]).ljust(8, b"\0"), f"btspell:{i}")


RANK_FIELD = 8
SPELL_RAW_REFS = [0x1FE36]  # new-game character record (bank 03): Kurt's first spell, ファイアボールA


def spell_refs(orig, region, bc, spells):
    """Copies of spell names in character records: an 8-byte field `name + rank capital + 0 pad` (ファイアボールA),
    in raw ROM (SPELL_RAW_REFS) and in the decompressed blocks (party members joining with spells).
    Returns [(block index or None, offset, spell n, rank byte)]."""
    by_name = {}
    for n, e in enumerate(spells, 1):
        by_name.setdefault(bc.encode(e["jp"]), n)

    def field(d, i):
        for enc, n in by_name.items():
            j = i + len(enc)
            if (d[i:j] == enc and j < i + RANK_FIELD and 0x41 <= d[j] <= 0x5A
                    and not any(d[j + 1:i + RANK_FIELD])):
                return n, d[j]
        return None

    out = []
    for off in SPELL_RAW_REFS:
        f = field(orig, off)
        assert f, f"spell record at {off:06X} moved"
        out.append((None, off, *f))
    firsts = {enc[0] for enc in by_name}
    for b in region.blocks:
        d = b.orig_data
        for i in range(len(d) - RANK_FIELD):
            if d[i] in firsts:
                f = field(d, i)
                if f:
                    out.append((b.index, i, *f))
    return out


def apply(orig, region, writer, files, alloc=None):
    """Splice every entry into region (block data) or writer (raw bytes). Strings longer than their slot move to
    TEXT_AREA through alloc, behind a far jump (and back); shorter ones jump over the rest. Returns the number of
    changed strings."""
    from textcodec import BG3_SPACE, bg3_en, bg3_jp
    changed = 0
    bc = ByteCodec(orig, JP)
    b3jp, b3en, b3sp = bg3_jp(orig), bg3_en(), BG3_SPACE.to_bytes(2, "little")
    names = NameTable(orig) if alloc is not None else None
    pools = BankPools()
    for name, doc in files.items():
        src = doc["source"]
        if src["kind"] == "battle":  # in place, same tile count (tools/battle_text.py)
            import battle_text
            for e in doc["entries"]:
                changed += bool(e["en"])
                writer.put(int(e["file"], 16), battle_text.encode(orig, e), f"text:{e['id']}")
            continue
        if src["kind"] == "bg3":
            moved = {w: {} for w in MOVED_WINDOWS}
            for e in doc["entries"]:
                changed += bool(e["en"])
                enc = b3en.encode(e["en"]) if e["en"] else b3jp.encode(e["jp"])
                off, size = int(e["file"], 16), e["size"]
                win = next((w for w in MOVED_WINDOWS if w[0] <= off < w[1]), None)
                if win:
                    moved[win][off] = (size, enc, e["id"])
                    continue
                if len(enc) > size and e["id"] in BG3_PTRS:
                    assert orig[off + size:off + size + 2] == b"\x00\xff", e["id"]
                    pools.repoint(off, enc + b"\x00\xff", {**e, "ptrs": BG3_PTRS[e["id"]]}, writer, orig)
                    continue
                ret = int(src["bank"], 16) << 16 | (int(e["addr"], 16) + size)
                writer.put(off, fit(enc, size, ret, alloc, writer, e["id"], b3sp), f"text:{e['id']}")
            for (lo, hi, ptr), subs in moved.items():
                if all(len(enc) <= size for size, enc, _ in subs.values()):
                    for o, (size, enc, eid) in subs.items():
                        ret = int(src["bank"], 16) << 16 | ((o + size) & 0x7FFF | 0x8000)
                        writer.put(o, fit(enc, size, ret, alloc, writer, eid, b3sp), f"text:{eid}")
                    continue
                out, o = bytearray(), lo
                while o < hi:
                    if o in subs:
                        out += subs[o][1]
                        o += subs[o][0]
                    else:
                        out += orig[o:o + 2]
                        o += 2
                assert orig[hi - 2:hi] == b"\x00\xff", f"window {lo:06X}"
                p = int(ptr, 16)
                assert int.from_bytes(orig[p:p + 2], "little") == (lo & 0x7FFF) | 0x8000, f"window pointer {ptr}"
                at = pools.place(lo & ~0x7FFF, bytes(out), f"window:{lo:06X}", writer)
                writer.put(p, ((at & 0x7FFF) | 0x8000).to_bytes(2, "little"), f"ptr:window:{lo:06X}")
            continue
        if src["kind"] == "block":
            b = region.blocks[src["block"]]
            assert f"{b.orig_off:06X}" == src["file"], f"{name}: block {src['block']} moved; re-run extract.py"
            data = bytearray(b.data)
        for n, e in enumerate(doc["entries"], 1):
            size = e["size"]
            changed += bool(e["en"])
            if src["kind"] == "names" and e["en"]:
                if names is None:
                    raise ValueError(f"{e['id']}: English byte names need the 4 MB build")
                assert n < 256, f"{name}: more than 255 names"
                esc = names.add(NAME_KIND[name], n, e["en"], e["id"])
                writer.put(int(e.get("field", e["file"]), 16), esc.ljust(e["max"], b"\0"), f"text:{e['id']}")
                continue
            enc = (bc if src["kind"] == "names" else EN if e["en"] else JP).encode(text_of(e))
            if src["kind"] == "names":
                if len(enc) > e["max"]:
                    raise ValueError(f"{e['id']}: {len(enc)} bytes > field {e['max']}")
                enc = enc.ljust(size if len(enc) <= size else e["max"], b"\0")
                writer.put(int(e["file"], 16), enc, f"text:{e['id']}")
                continue
            a = int(e["addr"], 16)
            if src["kind"] == "block":  # every block runs decompressed at $7F:0000 (rooms, common, shops)
                data[a:a + size] = fit(enc, size, 0x7F0000 | (a + size), alloc, writer, e["id"])
            else:
                ret = int(src["bank"], 16) << 16 | (a + size)
                if len(enc) > size and size < FAR_LEN and e.get("ptrs"):
                    pools.repoint(int(e["file"], 16), enc + far(ret), e, writer, orig)
                    continue
                writer.put(int(e["file"], 16), fit(enc, size, ret, alloc, writer, e["id"]), f"text:{e['id']}")
        if src["kind"] == "block":
            b.data = bytes(data)
    if names is not None:
        names.write(writer)
        window_headers(orig, writer)
        name_entry(writer)
        battle_bytes(writer)
        spells = files.get("spells", {"entries": []})["entries"]
        battle_spells(orig, writer, bc, spells)
        if any(e["en"] for e in spells):
            for bi, off, n, rank in spell_refs(orig, region, bc, spells):
                if not spells[n - 1]["en"]:
                    continue
                rec = bytes([NAME_KIND["spells"], n, rank]).ljust(RANK_FIELD, b"\0")
                if bi is None:
                    writer.put(off, rec, f"spellref:{off:06X}")
                else:
                    b = region.blocks[bi]
                    b.data = b.data[:off] + rec + b.data[off + RANK_FIELD:]
    return changed
