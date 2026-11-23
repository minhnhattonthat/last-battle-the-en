"""script_dis.py: disassemble the event-script VM (docs/re/text.md §Control codes) by following flow from entry points.

A script is a stream of 16-bit LE words read by 01:B79F: < $0300 BG3 tile, $0300-$07D0 glyph, >= $8000 control code
(high byte = op, low byte = argument), followed by 0+ argument BYTES (some ops take odd byte counts, so the stream is
not word-aligned). Argument layouts below were read off the handlers (tools/re_flow.py); "J" marks a 16-bit jump
target (an address inside the same script image, bank $7F for room blocks).

    python -X utf8 tools/script_dis.py                 # walk every room block, print a summary + all errors
    python -X utf8 tools/script_dis.py --room 1 -v     # listing for one room (entry index into table 0xD0081)
Library: decode(data, pos) and walk(data, entries, base) are used by the extractor."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from lz import decompress  # noqa: E402

ROM_PATH = ROOT / "rom" / "Last Battle, The (Japan).sfc"
OPS = bytes.fromhex("a0a1a3a4a5b0b1b2b3b4b5b6b7b8b9babbbcbdbec0c1c2d0d1d2d3d4d5d6d7d8e0e1e2e4e5e6ebeae9e8"
                    "eeedecef f4f5f6f8f9fafbfcfeff".replace(" ", ""))
GLYPH_MAX = 0x7D0
ROOM_TABLE, ROOM_COUNT = 0xD0081, 309


def lin2off(p):
    return 0xD0000 + (p - 0x1A8000)


def u16(d, i):
    return d[i] | d[i + 1] << 8


def args_layout(op, lo, d, p):
    """Argument layout for control word (op, lo) whose args start at d[p]. Returns a list of fields:
    'b' byte, 'w' word, 'J' jump-target word, 'T' terminal marker, ('jt', n) n-entry jump table (always jumps)."""
    if op == 0xA0:
        return ["b"]
    if op == 0xA1:
        return ["w", "b"]
    if op in (0xB4, 0xB5):
        return ["w"]
    if op == 0xB6:
        return [] if lo == 0xFF else ["w"]
    if op in (0xB7, 0xB8):
        return ["w", "b"] if lo == 0 else []
    if op == 0xBA:  # map change: returns 1 and the loop exits (room 136 ends on it)
        return ["w", "b", "b", "b", "b", "T"]
    if op == 0xBB:  # 01:BF77: lo 0-3 read 7 words (or skip them); 4, 5 none
        return ["w"] * 7 if lo < 4 else []
    if op == 0xE0:  # 01:D0C1: 00 jump, 01 call (B718), 02 jump table indexed by $A0 = menu choice after F8FF;
        # every E002 in the rooms has 3 targets (two options + cancel, checked: FB00 always follows).
        return {0: ["J", "T"], 1: ["J"], 2: [("jt", 3)]}.get(lo, [])
    if op == 0xBC:
        return ["b", "b"]
    if op == 0xBD:
        return [] if lo == 0xFF else ["b", "b", "w"]
    if op == 0xBE:
        return {0xF0: ["w"], 0xF1: ["w", "b"], 0xF2: ["w"]}.get(lo, [])
    if op == 0xD0:
        f = ["b"] * 7
        if p + 5 < len(d) and d[p + 5] & 0x70 in (0x10, 0x20):
            f += ["b"] * 4
        return f
    if op == 0xD1:
        if lo & 0x80:
            return ["b"]
        if p < len(d) and d[p] & 0x04:
            return ["b"]
        return ["b", "b"]
    if op == 0xD6:
        return ["b", "b", "b"]
    if op == 0xD7:
        return ["b", "b"]
    if op in (0xE1, 0xE2, 0xE8, 0xE9, 0xEA, 0xEB, 0xEC):
        return ["J"]
    if op == 0xED:
        return ["J"]
    if op == 0xEE:
        return ["w", "b", "J"] if lo == 0 else ["J"]
    if op == 0xE4:
        return ["b"]
    if op == 0xE6:
        return [("jt", lo)]
    if op == 0xEF:
        return ["N"]  # word: address of native 65816 code inside the image, run via JML [$0C04]
    if op == 0xFF:
        return ["T"]  # every FFxx ends the loop (tested: making FF01/FF02 fall through breaks 98 rooms)
    return []


def decode(d, pos):
    """One instruction at d[pos]. Returns dict(kind, word, op, lo, args, size, targets, terminal) or raises."""
    if pos + 2 > len(d):
        raise ValueError("runs past the end")
    w = u16(d, pos)
    if w < 0x8000:
        if 0x300 <= w <= GLYPH_MAX or w < 0x300:
            return {"kind": "glyph" if w >= 0x300 else "tile", "word": w, "size": 2, "targets": [], "terminal": False}
        raise ValueError(f"bad glyph {w:04X}")
    op, lo = w >> 8, w & 0xFF
    if op not in OPS:
        raise ValueError(f"unknown op {w:04X}")
    p = pos + 2
    args, targets, terminal = [], [], False
    for f in args_layout(op, lo, d, p):
        if f == "T":
            terminal = True
        elif f == "?":
            raise ValueError(f"unhandled layout {w:04X}")
        elif f == "b":
            args.append(d[p])
            p += 1
        elif f in ("w", "J", "N"):
            v = u16(d, p)
            args.append(v)
            if f == "J":
                targets.append(("J", v))
            elif f == "N":
                targets.append(("N", v))
            p += 2
        else:  # jump table
            n = f[1]
            for _ in range(n):
                v = u16(d, p)
                args.append(v)
                targets.append(("J", v))
                p += 2
            terminal = True
    if p > len(d):
        raise ValueError("args run past the end")
    return {"kind": "ctrl", "word": w, "op": op, "lo": lo, "args": args, "size": p - pos, "targets": targets,
            "terminal": terminal}


def walk(d, entries, base=0, overlap_ok=(), stop_at=()):
    """Flow walk from entries (image addresses). base = address of d[0]. Returns (instrs {pos: ins}, errors,
    native code addresses). overlap_ok: addresses a jump may hit inside another instruction (KNOWN_OVERLAPS);
    stop_at: addresses where a script runs off into data with no terminator (KNOWN_ENDS)."""
    instrs, errors, native, owner = {}, [], set(), {}
    todo = [e - base for e in entries]
    while todo:
        pos = todo.pop()
        while True:
            if pos in instrs:
                break
            if not 0 <= pos < len(d):
                errors.append(f"pos {pos + base:04X} outside image")
                break
            if pos + base in stop_at:
                break
            if pos in owner and pos + base not in overlap_ok:
                errors.append(f"{pos + base:04X} lands inside the instruction at {owner[pos] + base:04X}")
                break
            try:
                ins = decode(d, pos)
            except ValueError as e:
                errors.append(f"{pos + base:04X}: {e}")
                break
            clash = [q for q in range(pos + 1, pos + ins["size"]) if q in instrs]
            if clash and not overlap_ok:
                errors.append(f"{pos + base:04X} overlaps the instruction at {clash[0] + base:04X}")
            instrs[pos] = ins
            for q in range(pos + 1, pos + ins["size"]):
                owner[q] = pos
            for kind, t in ins["targets"]:
                if kind == "N":
                    native.add(t)
                else:
                    todo.append(t - base)
            if ins["terminal"]:
                break
            pos += ins["size"]
    return instrs, errors, native


EXTRA_ROOMS = list(range(29, 43))  # top-table entries (0xD0000) holding room-format blocks (via sub-tables 12, 13)
COMMON = 11  # top-table entry: shared script block; E5xx decompresses it over $7F0000 and runs its entry lo
# Top-table entries in the common-block format (word table of script pointers, 0 = unused, then scripts): shop,
# inn and healer scripts (docs/re/text.md §Where text lives). 16, 17, 22, 24-27 alias 14, 15, 21, 23.
COMMON_FORMAT = [11, 14, 15, 18, 19, 20, 21, 23, 28]


def top_ptr(rom, i):
    return lin2off(int.from_bytes(rom[0xD0000 + 3 * i:0xD0003 + 3 * i], "little"))


def room_block(rom, i):
    """Room i < 309: table 0xD0081; 309+: EXTRA_ROOMS; 'common': the E5 block; 'topN': top-table entry N."""
    if i == "common":
        off = top_ptr(rom, COMMON)
    elif isinstance(i, str) and i.startswith("top"):
        off = top_ptr(rom, int(i[3:]))
    elif i >= ROOM_COUNT:
        off = top_ptr(rom, EXTRA_ROOMS[i - ROOM_COUNT])
    else:
        off = lin2off(int.from_bytes(rom[ROOM_TABLE + 3 * i:ROOM_TABLE + 3 * i + 3], "little"))
    data, _ = decompress(rom, off)
    return off, data


def walk_common(d):
    """Common-format block: a word table of script pointers up to the first one (33 entries in the common block),
    no room header. A 0 word is an unused slot (top entries 20, 23)."""
    ents = [u16(d, i) for i in range(0, u16(d, 0), 2)]
    instrs, errors, native = walk(d, [e for e in ents if e])
    return instrs, errors, native, ents, []


def header(d):
    """Room block header: 9 words (docs/re/text.md §Room blocks). 0, 1: scripts (00:D656, 00:D634);
    2: talk list, one pointer per NPC to a 3-word table of scripts (first talk / flag $0534 set / talked before,
    01:A2DF); 3/4: search spots (x,y byte pairs, FF) + one script pointer per spot (01:C615); 5/6: spots + one
    event-script pointer per spot (00:C2C2); 7/8: spots + (flag, value) byte pairs (01:C6BD)."""
    return [u16(d, i) for i in range(0, 18, 2)]  # always 9 words (room 95's script starts at 0x13, not 0x12)


def spots(d, start):
    n = 0
    while start + 2 * n < len(d) and d[start + 2 * n] != 0xFF:
        n += 1
    return n


def talk_tables(d, hdr, code=frozenset()):
    """Talk list hdr[2]: pointers up to the first table it points at (or the block end). The NPC count is not
    stored (talk index = object id - 4, objects come from D0 commands), so the list also stops at the first word
    that can't be a table pointer, or at bytes already known to be code (`code`: offsets covered by a walk of the
    other entries): an empty list is followed directly by script code (E803 in room 15, text in room 118)."""
    out, p = [], hdr[2]
    end = min([h for h in hdr if h > hdr[2]] + [len(d)])
    while p + 2 <= end and p < min(out + [end]) and p not in code:
        t = u16(d, p)
        if not (p < t and t + 2 <= len(d) and 18 <= u16(d, t) < len(d)):
            break
        out.append(t)
        p += 2
    return out


def covered(d, instrs):
    out = set()
    for p, x in instrs.items():
        out.update(range(p, p + x["size"]))
    return out


def entries_of(d, soft=False):
    """Script entry addresses for a room block. soft=True returns the e6 step-trigger pointers instead: 00:C2C2
    uses them only when $2C != 0, and in some rooms (95) the words there are not pointers, so the caller keeps
    only those that decode cleanly."""
    hdr = header(d)
    n = spots(d, hdr[3])
    plain = hdr[:2] + [u16(d, hdr[4] + 2 * i) for i in range(n)]
    tables = talk_tables(d, hdr, covered(d, walk(d, plain)[0]))
    if soft:  # also talk-table words 2 and 3: room 149's table at 0090 has only two, script code follows
        n = spots(d, hdr[5])
        out = [u16(d, hdr[6] + 2 * i) for i in range(n) if hdr[6] + 2 * i + 2 <= len(d)]
        return out + [u16(d, t + 2 * i) for t in tables for i in (1, 2) if t + 2 * i + 2 <= len(d)]
    return plain + [u16(d, t) for t in tables]


KNOWN_OVERLAPS = {  # room: addresses where a jump lands inside another instruction, both decodings valid
    85: {0x95, 0x97},  # D008 at 008C: its b5 = $10 asks for 4 extension bytes (C10F FF00), yet E81E/EA0A jump to 0095
}
KNOWN_ENDS = {  # room: addresses where a script runs into data with no FFxx (left as in the original)
    310: {0x10D},  # search-spot text at 00F5 (both spots of e3) ends on 。 and runs into the e5 list
}


def data_ranges(d):
    """(start, length) of the header's data lists and talk tables (not script)."""
    hdr = header(d)
    out = [(0, 18)]
    n = spots(d, hdr[3])
    plain = hdr[:2] + [u16(d, hdr[4] + 2 * i) for i in range(n)]
    tables = talk_tables(d, hdr, covered(d, walk(d, plain)[0]))
    out.append((hdr[2], 2 * len(tables)))
    out += [(t, 6) for t in tables]
    for pos_k, ptr_k, width in ((3, 4, 2), (5, 6, 2), (7, 8, 2)):
        n = spots(d, hdr[pos_k])
        out += [(hdr[pos_k], 2 * n + 1), (hdr[ptr_k], width * n)]
    return out


def walk_room(d, room=None):
    """walk() over a room's entries plus every soft entry that decodes without errors.
    Returns (instrs, errors, native, entries, dropped soft entries)."""
    ents = entries_of(d)
    kw = {"overlap_ok": KNOWN_OVERLAPS.get(room, ()), "stop_at": KNOWN_ENDS.get(room, ())}
    dropped = []
    base = len(walk(d, ents, **kw)[1])
    for e in dict.fromkeys(entries_of(d, soft=True)):
        if e < 18 or e >= len(d) or len(walk(d, ents + [e], **kw)[1]) > base:
            dropped.append(e)
        else:
            ents.append(e)
    instrs, errors, native = walk(d, ents, **kw)
    return instrs, errors, native, ents, dropped


def fmt(ins):
    w = ins["word"]
    if ins["kind"] != "ctrl":
        return f"{w:04X}"
    return f"{w:04X} " + " ".join(f"{a:04X}" if a > 0xFF else f"{a:02X}" for a in ins["args"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--room", type=int)
    ap.add_argument("--top", help="a common-format top-table block: common, top14, top15 ... (COMMON_FORMAT)")
    ap.add_argument("-v", action="store_true")
    ap.add_argument("--gaps", action="store_true", help="list uncovered regions that look like text")
    a = ap.parse_args()
    gaps_text = []
    rom = ROM_PATH.read_bytes()
    rooms = ([a.top] if a.top else [a.room] if a.room is not None else
             list(range(ROOM_COUNT + len(EXTRA_ROOMS))) + ["common"] + [f"top{n}" for n in COMMON_FORMAT[1:]])
    tot_err = 0
    for i in rooms:
        off, d = room_block(rom, i)
        instrs, errors, native, ents, dropped = walk_common(d) if isinstance(i, str) else walk_room(d, i)
        covered = sum(x["size"] for x in instrs.values())
        tot_err += len(errors)
        if a.room is not None or a.top or errors or dropped:
            print(f"room {i!s:>6} @{off:06X} size {len(d):5d} entries {len(ents)} covered {covered:5d} "
                  f"({100 * covered // max(1, len(d) - 18)}%) native {sorted(native)} errors {len(errors)}"
                  + (f" dropped e6 {[hex(x) for x in dropped]}" if dropped else ""))
            for e in errors[:5]:
                print("    ", e)
        if a.gaps:
            cov = bytearray(len(d))
            for s, n in ([(0, 2 * len(ents))] if isinstance(i, str) else data_ranges(d)):
                cov[s:s + n] = b"\1" * len(cov[s:s + n])
            for p, x in instrs.items():
                cov[p:p + x["size"]] = b"\1" * x["size"]
            p = 0
            while p < len(d):
                if cov[p]:
                    p += 1
                    continue
                q = p
                while q < len(d) and not cov[q]:
                    q += 1
                text = max(sum(1 for k in range(s, q - 1, 2) if 0x334 <= u16(d, k) <= GLYPH_MAX) for s in (p, p + 1))
                if text >= 3:
                    gaps_text.append((i, p, q - p, text))
                p = q
        if a.v:
            for pos in sorted(instrs):
                print(f"  {pos:04X}  {fmt(instrs[pos])}")
    if a.gaps:
        for i, p, n, t in gaps_text:
            print(f"uncovered text? room {i} {p:04X} len {n} glyph-words {t}")
        print(len(gaps_text), "uncovered gaps with >= 3 kana/kanji words")
    print("total errors", tot_err)
    return 1 if tot_err else 0


if __name__ == "__main__":
    sys.exit(main())
