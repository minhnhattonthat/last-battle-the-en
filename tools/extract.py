"""extract.py: pull every string out of the ROM into script/*.json (docs/re/text.md §Where text lives).

Sources
  script blocks  every LZ block in room format (309 rooms + top 29-42) or common format (common, shops, inns,
                 healers), walked by tools/script_dis.py. File script/<name>.json, name = r<lowest room id> or the
                 top entry (common, top14 ...); ids <name>_<addr>, addr = offset in the decompressed image.
  bank04         uncompressed script in bank $04, walked from its pointer tables (B04_TABLES) and code immediates.
  credits        bank $02 staff roll, 24 pointers at 02:E215.
  items, spells  byte-encoded names in fixed 8-byte fields (ByteCodec).
  enemies, tactics  the same, FF-padded (battle name windows, 29:B2B6).

A string is a maximal run of walked instructions that are glyph words or no-argument controls (newline, page,
wait, name inserts...), trimmed to start and end on text; it is split at every entry point and jump target, so no
pointer lands inside a string. Terminators (FFxx) and every argument-bearing op stay outside, as code.
Text the walk never reaches (dead or reached from code not traced yet) is extracted too, with "reached": false.

    python -X utf8 tools/extract.py dump [--force]   # write script/*.json; existing files keep their "en"
    python -X utf8 tools/extract.py stats"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import blocks  # noqa: E402
import script_dis as S  # noqa: E402
from textcodec import JP, TOKEN, ByteCodec  # noqa: E402

ROM_PATH = ROOT / "rom" / "Last Battle, The (Japan).sfc"
SCRIPT = ROOT / "script"
TEXT_CTRL_OPS = {0xFE, 0xFA, 0xFC}  # controls that may start or end a string

# Bank $04 (file 0x20000-0x27FFF = $04:8000-$FFFF): pointer tables into its script, and where code reaches them.
B04_FILE, BANK_BASE = 0x20000, 0x8000
B04_TABLES = [  # (file offset, format, count or None = until terminator, what)
    (0x232D2, "ptr", 4, "party names (01:FBB1)"),
    (0x232FA, "pair", None, "(room, place name) pairs, FFFF end (01:B420, 01:B434; A4xx via $04:B2FC)"),
    (0x2364A, "ptr", 9, "chest / search messages and chest sub-scripts (01:A232, 01:C8F8)"),
    (0x2381C, "ptr", 9, "item and spell use messages (01:84DA, 01:934D)"),
    (0x2392C, "ptr", 2, "new-game script $04:B930"),
    (0x2398A, "ptr", 4, "mana names (01:FDA5)"),
    (0x239C4, "ptr", 11, "stat-up and sealing messages (01:933A)"),
    (0x23BB2, "triple", None, "(item id, description) triples, 00 end (01:9493)"),
    (0x24747, "ptr", 7, "equip-screen templates"),
    (0x247D9, "ptr", 5, "item category names, insert FA3E (item > Examine header)"),
    (0x24805, "ptr", 5, "stat names, insert FA3F (Examine stat line)"),
    (0x24831, "ptr", 2, "UP / DOWN, insert FA40 (Examine stat line)"),
]
B04_CODE_PTRS = [0x0A287]  # LDA #$B632 at 01:A286: "nobody here"
B04_DATA = [(0x23053, 0x231FC, "byte-to-glyph map / name-entry grid (01:FEE3)")]
B04_TEXT = (0x23053, 0x24845)  # the text area the coverage test sweeps (tile rows at 0x22CA7 are graphics)
B02_FILE = 0x10000
CREDITS_TABLE, CREDITS_N = 0x16215, 24
CREDITS_TEXT = (0x16245, 0x16878)
ITEM_LO, ITEM_HI, ITEM_STRIDE = 0x24AD1, 0x25201, 20
SPELLS, SPELL_N, SPELL_STRIDE = 0x14E20F, 28, 9
NAME_LEN = 8
# Battle names (docs/re/battle.md): FF-padded 8-byte fields, FF = blank (also inside a name and to centre it).
ENEMIES, ENEMY_N, ENEMY_STRIDE = 0x152634, 93, 40   # $2A:A632 + 40 * i (30:A915), name at record + 2
TACTICS, TACTIC_N, TACTIC_STRIDE = 0x1FEF0, 8, 12    # new-game copy to $1C91 (03:F8E9), name = first 8 bytes


def u16(d, i):
    return d[i] | d[i + 1] << 8


def is_text(ins):
    return ins["kind"] == "glyph" or (ins["kind"] == "ctrl" and ins["op"] in TEXT_CTRL_OPS and ins["size"] == 2)


def is_inline(ins):
    """May sit inside a string: glyph or tile words, or a control with no arguments that does not end the loop."""
    return ins["kind"] != "ctrl" or (ins["size"] == 2 and not ins["terminal"] and not ins["targets"])


def segment(d, instrs, targets, lo=0, hi=None):
    """(pos, size) of each string among instrs (positions in d) inside [lo, hi)."""
    hi = len(d) if hi is None else hi
    out, run = [], []

    def flush():
        while run and not is_text(instrs[run[-1]]):
            run.pop()
        while run and not is_text(instrs[run[0]]):
            run.pop(0)
        if any(instrs[p]["kind"] == "glyph" and instrs[p]["word"] != 0x300 for p in run):
            out.append((run[0], run[-1] + instrs[run[-1]]["size"] - run[0]))
        run.clear()

    for p in sorted(q for q in instrs if lo <= q < hi):
        ins = instrs[p]
        if run and (p != run[-1] + instrs[run[-1]]["size"] or p in targets):
            flush()
        if is_inline(ins):
            run.append(p)
        else:
            flush()
    flush()
    return out


def gap_runs(d, cov, lo=0, hi=None, min_kana=3):
    """Uncovered stretches of d holding >= min_kana kana/kanji words: [(start, end, alignment start)]."""
    hi = len(d) if hi is None else hi
    out, p = [], lo
    while p < hi:
        if cov[p]:
            p += 1
            continue
        q = p
        while q < hi and not cov[q]:
            q += 1
        best = max((sum(1 for k in range(s, q - 1, 2) if 0x334 <= u16(d, k) <= S.GLYPH_MAX), s) for s in (p, p + 1))
        if best[0] >= min_kana:
            out.append((p, q, best[1]))
        p = q
    return out


def strings_of(d, instrs, entries, base, cov_extra=()):
    """Walked strings plus unreached text in the gaps. Returns [(pos, size, reached)]."""
    targets = {e - base for e in entries}
    for x in instrs.values():
        targets.update(t - base for _, t in x["targets"])
    out = [(p, n, True) for p, n in segment(d, instrs, targets)]
    cov = bytearray(len(d))
    for s, n in cov_extra:
        cov[s:s + n] = b"\1" * len(cov[s:s + n])
    for p, x in instrs.items():
        cov[p:p + x["size"]] = b"\1" * x["size"]
    for g0, g1, start in gap_runs(d, cov):
        gi, starts, pos = {}, set(), start  # decode as script from the gap start, never past its end; a
        while pos + 2 <= g1:                # terminator (FF00 before the text) restarts the walk after it
            starts.add(pos)
            got, _, _ = S.walk(d[:g1], [pos])
            gi.update(got)
            pos = max((p + x["size"] for p, x in got.items()), default=pos + 2)
        out += [(p, n, False) for p, n in segment(d, gi, starts, g0, g1)]
    return sorted(out)


def entry(src, pos, size, data, reached=True, addr_base=0, **extra):
    e = {"id": f"{src}_{pos + addr_base:04X}", "addr": f"{pos + addr_base:04X}", "size": size,
         "jp": JP.decode(data[pos:pos + size]), "en": ""}
    if not reached:
        e["reached"] = False
    e.update(extra)
    return e


def block_name(b):
    rooms = [(s - blocks.ROOMS) // 3 for s in b.slots if s >= blocks.ROOMS]
    tops = [(s - blocks.TOP) // 3 for s in b.slots if s < blocks.ROOMS]
    rooms += [S.ROOM_COUNT + S.EXTRA_ROOMS.index(t) for t in tops if t in S.EXTRA_ROOMS]
    if rooms:
        return f"r{min(rooms):03d}", "room", min(rooms)
    common = [t for t in tops if t in S.COMMON_FORMAT]
    if common:
        return ("common" if S.COMMON in common else f"top{min(common)}"), "common", None
    return None, None, None


def block_sources(rom, region=None):
    """{name: (block, instrs, entries, cov_extra)} for every script block."""
    region = region or blocks.unpack(rom)
    out = {}
    for b in region.blocks:
        name, fmt, room = block_name(b)
        if not name:
            continue
        d = b.orig_data
        if fmt == "room":
            instrs, errors, _, ents, _ = S.walk_room(d, room)
            extra = S.data_ranges(d)
        else:
            instrs, errors, _, ents, _ = S.walk_common(d)
            extra = [(0, 2 * len(ents))]
        assert not errors, (name, errors[:3])
        out[name] = (b, instrs, ents, extra)
    return out


def bank04_tables(rom):
    """[(table file offset, slot file offset, target $04 address)] and the data ranges the tables occupy."""
    slots, data = [], []
    for off, fmt, n, _ in B04_TABLES:
        p, k = off, 0
        while n is None or k < n:
            if fmt == "ptr":
                slots.append((off, p, u16(rom, p)))
                p += 2
            elif fmt == "pair":
                if u16(rom, p) == 0xFFFF:
                    p += 2
                    break
                slots.append((off, p + 2, u16(rom, p + 2)))
                p += 4
            else:
                if rom[p] == 0:
                    p += 1
                    break
                slots.append((off, p + 1, u16(rom, p + 1)))
                p += 3
            k += 1
        data.append((off, p))
    for p in B04_CODE_PTRS:
        slots.append((None, p, u16(rom, p)))
    return slots, data


def raw_strings(rom, file_base, ptr_slots, data_ranges, text_range, src):
    """Walk a raw bank (file_base = $xx:8000) from pointer slots [(table, slot, addr)]; entries with their slots."""
    d = rom[file_base:file_base + 0x8000]
    ents = sorted({a for _, _, a in ptr_slots})
    instrs, errors, _ = S.walk(d, ents, BANK_BASE)
    assert not errors, (src, errors[:3])
    cov_extra = [(s - file_base, e - s) for s, e, *_ in data_ranges]
    lo, hi = (x - file_base for x in text_range)
    cov_extra += [(0, lo), (hi, len(d) - hi)]  # sweep for unreached text only inside the text area
    out = []
    for pos, size, reached in strings_of(d, instrs, [e for e in ents], BANK_BASE, cov_extra):
        ptrs = [f"{s:06X}" for _, s, a in ptr_slots if a == pos + BANK_BASE]
        out.append(entry(src, pos, size, d, reached, BANK_BASE, file=f"{file_base + pos:06X}", ptrs=ptrs))
    return out


B04_BG3 = (0x20600, 0x22CA7)  # BG3 tile-word strings (menu prompts/labels, description boxes); 0x20400-0x205FF
# is the debug flag viewer (hex grid) and 0x22CA7 on the name-entry grid rows (graphics, handled with the name maps)
BG3_MIN_KANA = 2
# Description boxes (width gate, docs/re/windows.md; measured 2026-11-24, work/qa/desc*): $04 address ranges ->
# (box, tiles per line, lines). Item descriptions show in the item shop's panel (5 x 7: a 6th tile lands on the
# right frame; tour8 svc_00/svc_01, session 35) and the field item menu (6 x 7): the narrower one binds. The game
# also writes a blank tile after the last character, so an item description's last line holds one tile fewer
# (DESC_LAST_SHORT; a 5-tile "30 HP" broke the shop frame). Spell descriptions: 7 tiles; label lines keep tiles
# 0-3, the game draws the value at 4-5. $A6ED (equip stat labels) is a template, not a description.
DESC_BOXES = [(0xA331, 0xA6ED, ("desc_item", 5, 7)), (0xA751, 0xA8EB, ("desc_item", 5, 7)),
              (0xA8EB, 0xAC9F, ("desc_spell", 7, 4))]
DESC_LAST_SHORT = {"desc_item"}


def desc_box(addr):
    """(box, tiles, lines) of the description box a BG3 string at $04 `addr` shows in, or None."""
    return next((b for lo, hi, b in DESC_BOXES if lo <= addr < hi), None)


def bg3_strings(rom, lo=B04_BG3[0], hi=B04_BG3[1]):
    """Tile-word strings in [lo, hi) of bank 04: decoded linearly as VM script (resyncing a byte at a time over data
    the decoder refuses, restarting after every instruction), a string is a run of tile words and argument-free FA/FE
    words holding >= BG3_MIN_KANA kana tiles and no glyph word. Checked against the VM's reads (01:B7A1) in the menu
    scenes: every read range starts at a string or a window script, never inside a string."""
    from textcodec import bg3_jp, bg3_tiles
    jp = bg3_jp(rom)
    kana = {t for t, c in bg3_tiles(rom).items() if "ぁ" <= c <= "ヶ" and c != "・"}
    instrs, pos = {}, lo
    while pos < hi:
        try:
            ins = S.decode(rom, pos)
        except ValueError:
            # a window script after an FF00 end starts with a 4-byte header (`xx yy hh ww`): skip it whole, as a
            # byte-at-a-time resync can swallow the script's first tiles (the status screen's `↓まほう` lost its ま)
            prev = instrs.get(pos - 2)
            hdr = rom[pos:pos + 4]
            header = (prev and prev.get("word") == 0xFF00 and hdr[0] < 0x20 and hdr[1] < 0x20
                      and 0 < hdr[2] <= 0x20 and 0 < hdr[3] <= 0x20)
            pos += 4 if header else 1
            continue
        if pos + ins["size"] > hi:
            break
        instrs[pos] = ins
        pos += ins["size"]
    runs, run = [], []
    for p in sorted(instrs):
        x = instrs[p]
        inline = x["kind"] == "tile" or (x["kind"] == "ctrl" and x["size"] == 2 and x["op"] in (0xFA, 0xFE))
        if inline and run and p == run[-1] + instrs[run[-1]]["size"]:
            run.append(p)
            continue
        runs.append(run)
        run = [p] if inline else []
    runs.append(run)
    out = []
    for r in runs:
        while r and instrs[r[-1]]["kind"] == "ctrl" and instrs[r[-1]]["op"] == 0xFE:
            r = r[:-1]
        while r and instrs[r[0]]["kind"] == "ctrl" and instrs[r[0]]["op"] == 0xFE:
            r = r[1:]
        if sum(instrs[p]["word"] in kana for p in r) < BG3_MIN_KANA:
            continue
        pos, size = r[0], r[-1] + 2 - r[0]
        text = jp.decode(rom[pos:pos + size])
        width = max(len(TOKEN.sub("", ln)) for ln in text.split("{nl}"))
        addr = pos - B04_FILE + BANK_BASE
        e = {"id": f"bg3_{addr:04X}", "addr": f"{addr:04X}",
             "size": size, "jp": text, "en": "", "file": f"{pos:06X}", "tiles": width}
        box = desc_box(addr)
        if box and "{nl}" in text:
            e["box"], e["max_tiles"], e["max_lines"] = box
        out.append(e)
    return out


def name_entries(rom, bc, src, offsets):
    out = []
    for key, off in offsets:
        raw = rom[off:off + NAME_LEN]
        n = raw.index(0) if 0 in raw else NAME_LEN
        if n == 0:
            continue
        out.append({"id": f"{src}_{key}", "file": f"{off:06X}", "size": n, "max": NAME_LEN,
                    "jp": bc.decode(raw[:n]), "en": ""})
    return out


def padded_entries(rom, bc, src, offsets):
    """FF-padded name fields: the string is the field without its leading and trailing FF ("field" = the field's
    start, where the English escape goes)."""
    out = []
    for key, off in offsets:
        raw = rom[off:off + NAME_LEN]
        lead = len(raw) - len(raw.lstrip(b"\xff"))
        body = raw.strip(b"\xff")
        if not body:
            continue
        out.append({"id": f"{src}_{key}", "file": f"{off + lead:06X}", "field": f"{off:06X}", "size": len(body),
                    "max": NAME_LEN, "jp": bc.decode(body), "en": ""})
    return out


def extract_all(rom):
    """{file name: {"source": ..., "entries": [...]}}"""
    files = {}
    for name, (b, instrs, ents, extra) in block_sources(rom).items():
        es = [entry(name, p, n, b.orig_data, r) for p, n, r in strings_of(b.orig_data, instrs, ents, 0, extra)]
        if es:
            files[name] = {"source": {"kind": "block", "block": b.index, "file": f"{b.orig_off:06X}",
                                      "slots": blocks.kind(rom, b)}, "entries": es}
    slots, data = bank04_tables(rom)
    files["bank04"] = {"source": {"kind": "raw", "file": f"{B04_FILE:06X}", "bank": "04"},
                       "entries": raw_strings(rom, B04_FILE, slots, data + B04_DATA, B04_TEXT, "b04")}
    files["menus"] = {"source": {"kind": "bg3", "file": f"{B04_FILE:06X}", "bank": "04"},
                      "entries": bg3_strings(rom)}
    cslots = [(CREDITS_TABLE, CREDITS_TABLE + 2 * i, u16(rom, CREDITS_TABLE + 2 * i)) for i in range(CREDITS_N)]
    files["credits"] = {"source": {"kind": "raw", "file": f"{B02_FILE:06X}", "bank": "02"},
                        "entries": raw_strings(rom, B02_FILE, cslots, [], CREDITS_TEXT, "cr")}
    bc = ByteCodec(rom, JP)
    # 01:8B2D takes index < $C0 from ITEM_LO, yet ITEM_LO + 20 * $5C = ITEM_HI: indices $5C-$BF alias the key-item
    # records (or other data past them), so each record is listed once, under its real index.
    items = ([(f"{i:02X}", ITEM_LO + ITEM_STRIDE * i) for i in range((ITEM_HI - ITEM_LO) // ITEM_STRIDE)]
             + [(f"{i:02X}", ITEM_HI + ITEM_STRIDE * (i - 0xC0)) for i in range(0xC0, 0x100)])
    files["items"] = {"source": {"kind": "names", "record": ITEM_STRIDE}, "entries": name_entries(rom, bc, "item", items)}
    spells = [(f"{i:02d}", SPELLS + SPELL_STRIDE * i) for i in range(SPELL_N)]
    files["spells"] = {"source": {"kind": "names", "record": SPELL_STRIDE},
                       "entries": name_entries(rom, bc, "spell", spells)}
    enemies = [(f"{i:02d}", ENEMIES + ENEMY_STRIDE * i) for i in range(ENEMY_N)]
    files["enemies"] = {"source": {"kind": "names", "record": ENEMY_STRIDE, "pad": "FF"},
                        "entries": padded_entries(rom, bc, "enemy", enemies)}
    tactics = [(f"{i}", TACTICS + TACTIC_STRIDE * i) for i in range(TACTIC_N)]
    files["tactics"] = {"source": {"kind": "names", "record": TACTIC_STRIDE, "pad": "FF"},
                        "entries": padded_entries(rom, bc, "tactic", tactics)}
    import battle_text
    files["battle"] = {"source": {"kind": "battle"}, "entries": battle_text.entries(rom)}
    return files


def coverage(rom, files=None):
    """Problems (list of str) found against the ORIGINAL ROM:
    - a walked glyph word outside every string; strings that overlap;
    - a kana/kanji word in any text run tools/re_textscan.py finds (>= 3 glyphs, both alignments) in a script block
      or in the raw text areas (bank $04 B04_TEXT, credits) that is outside every string and every known data range."""
    from re_textscan import runs
    files = files or extract_all(rom)
    probs = []

    def check(name, d, spans, instrs, data=()):
        cov = bytearray(len(d))
        last = -1
        for s, n in sorted(spans):
            if s < last:
                probs.append(f"{name}: string at {s:04X} overlaps the previous one")
            last = s + n
            cov[s:s + n] = b"\1" * n
        dcov = bytearray(cov)
        for s, n in data:
            dcov[s:s + n] = b"\1" * len(dcov[s:s + n])
        for p, x in (instrs or {}).items():
            if x["kind"] == "glyph" and x["word"] != 0x300 and not cov[p]:
                probs.append(f"{name}: walked glyph at {p:04X} is in no string")
            dcov[p:p + x["size"]] = b"\1" * x["size"]  # code and its argument bytes are not text
        for s, e, _, words in runs(bytes(d)):
            miss = [s + 2 * k for k, w in enumerate(words)
                    if 0x334 <= w <= S.GLYPH_MAX and not (dcov[s + 2 * k] or dcov[s + 2 * k + 1])]
            if len(miss) >= 3:
                probs.append(f"{name}: text run {s:04X}-{e:04X} has {len(miss)} kana/kanji outside strings")

    for name, (b, instrs, ents, extra) in block_sources(rom).items():
        spans = [(int(e["addr"], 16), e["size"]) for e in files.get(name, {"entries": []})["entries"]]
        check(name, b.orig_data, spans, instrs, extra)
    slots, data = bank04_tables(rom)
    for name, fbase, (lo, hi), drs in (("bank04", B04_FILE, B04_TEXT, data + B04_DATA),
                                       ("credits", B02_FILE, CREDITS_TEXT, [])):
        d = rom[lo:hi]
        spans = [(int(e["file"], 16) - lo, e["size"]) for e in files[name]["entries"]]
        check(name, d, spans, None, [(s - lo, e - s) for s, e, *_ in drs])
    return probs


RENAMED = {"bt_198956": "bt_19895C", "bt_198986": "bt_198988"}  # new id: old id (battle_text.EXTRA_RECTS, s27)


def write(files, force=False):
    SCRIPT.mkdir(exist_ok=True)
    wrote = kept = 0
    for name, doc in files.items():
        path = SCRIPT / f"{name}.json"
        if path.exists():
            if not force:
                kept += 1
                continue
            old = {e["id"]: e for e in json.loads(path.read_text(encoding="utf-8"))["entries"]}
            for new_id, old_id in RENAMED.items():  # an entry whose geometry (and so id) was corrected
                if old_id in old and new_id not in old:
                    old[new_id] = old.pop(old_id)
            for e in doc["entries"]:
                for k in ("en", "notes", "status"):
                    if old.get(e["id"], {}).get(k):
                        e[k] = old[e["id"]][k]
            lost = [i for i, e in old.items() if e.get("en") and i not in {x["id"] for x in doc["entries"]}]
            if lost:
                raise SystemExit(f"{path}: --force would drop English for {lost[:5]}")
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        wrote += 1
    print(f"wrote {wrote} files, kept {kept} existing (use --force to refresh, English is preserved)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["dump", "stats", "coverage"])
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    files = extract_all(ROM_PATH.read_bytes())
    if a.cmd == "dump":
        write(files, a.force)
    if a.cmd == "coverage":
        probs = coverage(ROM_PATH.read_bytes(), files)
        print("\n".join(probs[:60]))
        print(len(probs), "coverage problems")
    n = sum(len(f["entries"]) for f in files.values())
    unreached = sum(1 for f in files.values() for e in f["entries"] if e.get("reached") is False)
    chars = sum(len(e["jp"]) for f in files.values() for e in f["entries"])
    print(f"{len(files)} files, {n} strings ({unreached} unreached), {chars} characters of JP")


if __name__ == "__main__":
    main()
