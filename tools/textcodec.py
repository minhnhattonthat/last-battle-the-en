"""textcodec.py: script text <-> bytes for The Last Battle (docs/re/text.md §Encoding).

Script text is 16-bit LE words. Glyph words ($0300-$07D0) decode through tbl/jp.tbl; the control words that can sit
inside a string (newline, page, wait, name inserts) decode to the names in CTRL; any other word (a tile word < $0300,
an unnamed control, the second code of a glyph the font holds twice) decodes to `{XXXX}` (4 upper-case hex digits)
so decode -> encode is byte-exact.

Byte names (items, spells, party names in save records) use the 1-byte encoding of 01:FEE3: byte b >= $2C -> the
glyph word at file 0x23053 + 2 * (b - $2C); a 0 byte ends a name. Unmapped bytes decode as `[XX]`.

    from textcodec import JP
    text = JP.decode(words_bytes); assert JP.encode(text) == words_bytes"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CTRL = {  # names are provisional where docs/re/text.md marks the meaning as a guess
    0xFE00: "nl", 0xFE01: "page", 0xFE02: "page2", 0xFCFF: "wait",
    0xFA38: "actor", 0xFA39: "spell", 0xFA3A: "item", 0xFA3B: "num", 0xFA47: "target", 0xFA4F: "spell2",
}
TOKEN = re.compile(r"\{([0-9A-F]{4}|[a-z][a-z0-9]*)\}|\[([0-9A-F]{2})\]")
BYTE_MAP_OFF, BYTE_MAP_FIRST = 0x23053, 0x2C


def load_tbl(path=ROOT / "tbl" / "jp.tbl"):
    """{word: char} for single-character glyph entries of a Thingy table with 2-byte LE keys."""
    out = {}
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        key, sep, val = line.partition("=")
        if line.startswith("#") or not sep or len(key) != 4:
            continue
        val = " " if val == r"\s" else val
        if val.startswith("{"):
            continue
        out[int.from_bytes(bytes.fromhex(key), "little")] = val
    return out


class WordCodec:
    def __init__(self, glyphs):
        self.dec = dict(glyphs)
        self.enc = {}
        for w, ch in sorted(self.dec.items()):
            self.enc.setdefault(ch, w)
        self.ctrl_enc = {v: k for k, v in CTRL.items()}
        self.maxlen = max(map(len, self.enc))

    def word(self, w):
        if w in CTRL:
            return "{" + CTRL[w] + "}"
        ch = self.dec.get(w)
        if ch is not None and self.enc[ch] == w and not ch.startswith(("{", "[")):
            return ch
        return f"{{{w:04X}}}"

    def decode(self, data):
        if len(data) % 2:
            raise ValueError("odd byte count")
        return "".join(self.word(data[i] | data[i + 1] << 8) for i in range(0, len(data), 2))

    def words(self, text):
        out, i = [], 0
        while i < len(text):
            m = TOKEN.match(text, i)
            if m:
                if m[2]:
                    raise ValueError(f"byte escape [{m[2]}] in word text {text!r}")
                t = m[1]
                if t in self.ctrl_enc:
                    out.append(self.ctrl_enc[t])
                elif re.fullmatch(r"[0-9A-F]{4}", t):
                    out.append(int(t, 16))
                else:
                    raise ValueError(f"unknown control {{{t}}} in {text!r}")
                i = m.end()
                continue
            for k in range(min(self.maxlen, len(text) - i), 0, -1):
                if text[i:i + k] in self.enc:
                    out.append(self.enc[text[i:i + k]])
                    i += k
                    break
            else:
                raise ValueError(f"unencodable {text[i]!r} at {i} in {text!r}")
        return out

    def encode(self, text):
        return b"".join(w.to_bytes(2, "little") for w in self.words(text))


class ByteCodec:
    """1-byte name encoding; the map comes from the ROM's byte-to-glyph table."""

    def __init__(self, rom, words):
        self.dec = {}
        for b in range(BYTE_MAP_FIRST, 0x100):
            p = BYTE_MAP_OFF + 2 * (b - BYTE_MAP_FIRST)
            w = rom[p] | rom[p + 1] << 8
            ch = words.dec.get(w)
            if 0x300 <= w <= 0x7D0 and ch and len(ch) == 1:
                self.dec[b] = ch
        self.enc = {}
        for b, ch in sorted(self.dec.items()):
            self.enc.setdefault(ch, b)

    def decode(self, data):
        return "".join(self.dec[b] if b in self.dec and self.enc[self.dec[b]] == b else f"[{b:02X}]" for b in data)

    def encode(self, text):
        out, i = bytearray(), 0
        while i < len(text):
            m = TOKEN.match(text, i)
            if m and m[2]:
                out.append(int(m[2], 16))
                i = m.end()
            elif text[i] in self.enc:
                out.append(self.enc[text[i]])
                i += 1
            else:
                raise ValueError(f"unencodable {text[i]!r} at {i} in {text!r}")
        return bytes(out)


JP = WordCodec(load_tbl())

# English: printable ASCII c -> word EN_BASE + c, drawn by the VWF (asm/vwf.asm, font tools/font_en.txt)
EN_BASE = 0x0800
EN = WordCodec({EN_BASE + c: chr(c) for c in range(0x20, 0x7F)})

# BG3 tile words (< $0300, 8x8 fixed tiles written straight to the BG3 map by the VM, 01:B7D1): menu prompts and
# labels, description boxes in bank 04 (docs/re/text.md §BG3 strings). Tile -> kana through the byte maps of 01:FEAA
# ($04:AEAB, byte -> tile) and 01:FEE3 ($04:B053, byte -> glyph word). English: digits and capitals are tiles
# $01-$24, lowercase and `',.-!?&/:+` the tiles tools/font_bg3.py draws over the hiragana, space tile $93.
BG3_MAP_OFF = 0x22EAB
BG3_SPACE = 0x93


def bg3_tiles(rom):
    """{tile word: char} for every tile the byte maps name (first byte wins)."""
    out = {}
    for i in range(0x100 - BYTE_MAP_FIRST):
        t = rom[BG3_MAP_OFF + 2 * i] | rom[BG3_MAP_OFF + 2 * i + 1] << 8
        g = rom[BYTE_MAP_OFF + 2 * i] | rom[BYTE_MAP_OFF + 2 * i + 1] << 8
        ch = JP.dec.get(g)
        if t < 0x300 and ch and len(ch) == 1 and JP.enc.get(ch) == g:
            out.setdefault(t, ch)
    return out


def bg3_jp(rom):
    """Japanese side of BG3 strings: tile words decode to kana (a glyph word with the same character decodes to
    `{XXXX}`, so decode -> encode stays byte-exact)."""
    return WordCodec({**JP.dec, **bg3_tiles(rom)})


def bg3_en():
    """English side of BG3 strings: printable ASCII the BG3 font can show -> tile word."""
    import font_bg3
    m = {BG3_SPACE: " "}
    m.update({1 + i: str(i) for i in range(10)})
    m.update({0x0B + i: chr(0x41 + i) for i in range(26)})
    m.update({t: c for c, t in font_bg3.TILE.items()})
    return WordCodec(m)
