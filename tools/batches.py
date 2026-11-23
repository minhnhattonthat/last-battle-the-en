"""Translation batches (docs/translator-brief.md): split untranslated text, check translator output, merge it back.

    python -X utf8 tools/batches.py split [--size 3500]   work/tl/bNNN.tsv and build/terms_bNNN.txt for untranslated JP
    python -X utf8 tools/batches.py check [bNNN ...]      a batch's .out.tsv; with no batch, all shipped English (check.py)
    python -X utf8 tools/batches.py merge bNNN ... [--overwrite]   check, then write the English into script/
    python -X utf8 tools/batches.py show bNNN             the out.tsv after wrapping, one line per box line (dry run)
    python -X utf8 tools/batches.py fit "English text" [--form dlg]   wrapped lines with their pixel widths

Adapted from the skill's assets/batches.py. Batch TSV: id, speaker, form, limit, JP. Output: work/tl/bNNN.out.tsv,
id<TAB>English, every id once, same order. Dialogue forms are wrapped here: a page (text between {page}/{page2}) with
no {nl} is wrapped greedily to the box width; a page with {nl} keeps the translator's breaks. In an entry whose
English starts with `"`, every line not starting with `"` gets one leading space (the JP 「 indent).
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
TL = ROOT / "work/tl"
SCRIPT = ROOT / "script"
GLOSSARY = ROOT / "glossary.md"
MAX_ENTRIES = 150

# ---- ADAPTER: this game's text format ----
TOKEN = re.compile(r"\{[0-9A-Za-z]+\}|\[[0-9A-F]{2}\]")
FREE = {"{nl}", "{page}", "{wait}"}  # layout codes the English may place freely
VARIABLE = r"\{num\}"
# D1 keeps honorifics on names (glossary.md Rulings): a katakana name + honorific needs the EN suffix.
HONORIFICS = {"様": "sama", "さま": "sama", "さん": "san", "ちゃん": "chan", "くん": "kun", "君": "kun",
              "殿": "dono", "どの": "dono", "先生": "sensei"}
HONORIFIC_RE = re.compile(r"([ァ-ヶ][ァ-ヶー－]+)(" + "|".join(sorted(HONORIFICS, key=len, reverse=True)) + ")")
HONORIFIC_NOT_NAMES = {"オレ", "バア", "ヨメ", "ネ－", "ネー"}  # オレ様, バアさん, ヨメさん, ネーちゃん: not names
HONORIFIC_TITLES = ("城将", "枢機卿", "卿")  # a title before the name: the English title replaces the honorific
HONORIFIC_WAIVED = {"top15_03B6"}  # shop clerk addressing the hero: drops -san like the {actor} shop template
DLG_PX = 208  # dialogue box 216 px (docs/re/windows.md), edge pixel kept free
INSERT_PX = {"{actor}": 48, "{target}": 48, "{item}": 54, "{spell}": 54, "{spell2}": 54, "{num}": 24}
BG3_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz',.-!?&/:+ ")
BANNERS = (0xB3B0, 0xB631)  # bank-04 place-name banners, 144 px, centred with leading spaces
CHAR_NAMES = ("b04_B2DA", "b04_B2E2", "b04_B2E8", "b04_B2F0")
NAME_CAP = 9  # item names (D18): 9 tiles in every list (field item windows widened in phase 7, shop list 9)
TACTIC_CAP = 8  # tactics names (D18): the field tactics list (01:FE7A, LDA #8) has the formation icons right after it
LAYOUT_FREE = ("battle",)
# BG3 strings that share one list window: the cap is the window's widest JP entry, not the string's own length
# (phase-8 visual check: the teleport list holds 9-letter names; shop commands 4; one-word item notes in the 6-wide box)
MENU_CAP = {**{f"bg3_{a}": 9 for a in "A1B6 A1C6 A1D8 A1E2 A1EC A1FA A20A A218 A226 A238 A242 A24A A258 A264 A272 "
                                     "A27E".split()},
            "bg3_9EF0": 4, "bg3_9EF8": 4, "bg3_8F1C": 3, "bg3_A65D": 6, "bg3_A687": 6,
            "bg3_A729": 4, "bg3_A737": 4, "bg3_A73D": 4}  # forms whose JP layout tokens (dakuten rows {2094}...) the English may drop
# 2-tile slots the build moves whole (insert.BG3_PTRS, insert.MOVED_WINDOWS; D18): no slot limit, at most this many lines
REPOINTED = {"bg3_9EF0": 1, "bg3_9EF8": 1, "bg3_A687": 7, "bg3_A729": 1, "bg3_A737": 1, "bg3_A73D": 1}
# Name inserts in BG3 messages at their longest English width (asm nm_feaa): FA18 item name 9 (D18, return $FC70),
# character names 8 (FA0F/FA42 via 01:FE3B, spell names FA2B/FA2F 8). The JP drew every one of them at 8.
INSERT_TILES = {"{FA18}": NAME_CAP, "{FA0F}": 8, "{FA42}": 8, "{FA2B}": 8, "{FA2F}": 8}
# The one-line prompt box at the top of the field menus ("Do what with items?", "Gave X to Y."): 26 tiles inside
# (measured: work/qa/i1d, text column 0 at x=24, right border tile at x=232)
# Also the centred prompts shown there: wrap() centres them on the JP text's centre, up to this width (not the JP
# string's own tile count, which put "Are you sure?" 2.5 tiles left of the JP; inkbox on work/qa/tour2, b067).
MSG_BOX = {f"bg3_{a}": 26 for a in (
    "86A6 87A6 8886 892A 8ADA 8BFA 8C1A 8C3A 8C64 8D56 8E26 8E44 "
    "8600 8622 8652 8724 877E 87D2 8800 882C 88B0 8906 894A 89D2 8A12 8A3E 8A62 8A86 8B06 8B30 8B58 8BCC 8C3A 8CB2 "
    "8CDC 8D30 8DA4 8DCE").split()}
_ROM = None


def rom():
    global _ROM
    if _ROM is None:
        _ROM = next((ROOT / "rom").glob("*.sfc")).read_bytes()
    return _ROM


def docs():
    for path in sorted(SCRIPT.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        kind = doc["source"]["kind"]
        for e in doc["entries"]:
            e.setdefault("_file", path.stem)
            e.setdefault("_kind", kind)
        yield path, doc, doc["entries"]


def form(e):
    f, k = e["_file"], e["_kind"]
    if k == "names":
        return "name"
    if k == "bg3":
        return "menu"
    if k == "battle":
        return "battle"
    if f == "credits":
        return "credit"
    if e["id"] in CHAR_NAMES:
        return "charname"
    if f == "bank04" and BANNERS[0] <= int(e["addr"], 16) <= BANNERS[1]:
        return "banner"
    if f == "r320":
        return "epilogue"
    return "dlg"


def needs_english(entry):
    return bool(entry.get("jp")) and not entry.get("en")


def group_of(entry):
    return entry.get("dup") or entry["id"]


def entry_key(entry):
    return entry["id"]


def limit_label(e):
    f = form(e)
    if f == "dlg":
        return f"{DLG_PX}px x3"
    if f == "epilogue":
        return f"{DLG_PX}px"
    if f == "banner":
        return "144px, centre with leading spaces"
    if f == "credit":
        return "192px per line"
    if f == "charname":
        return "8 chars"
    if f == "menu":
        if e.get("max_tiles"):
            return f"{e['max_tiles']} chars x {e['max_lines']} lines"
        return f"{e['tiles']} chars per line, keep the line count"
    if f == "battle":
        return f"{e['w']} chars x {e['h']} rows"
    if f == "name":
        return {"enemies": "2 rows of 8 (split at a space), 16 max", "spells": "8 chars, plus ' A' rank in battle",
                "items": f"{NAME_CAP} chars", "tactics": f"{TACTIC_CAP} chars"}[e["_file"]]
    return ""


def px(text):
    from font_en import ADVANCE
    w = 0
    for m in re.finditer(r"\{[0-9A-Za-z]+\}|.", text):
        t = m[0]
        # {XXXX} words: $C000+ are script controls (wait, page, sound, position: no width), the rest 12 px glyphs
        # except {FAxx}: name/number inserts (an 8-letter name, about 56 px)
        glyph = len(t) == 6 and t[1] not in "CDEF"
        dflt = 56 if t.startswith("{FA") else 12 if glyph else 0
        w += INSERT_PX.get(t, dflt) if t[0] == "{" and len(t) > 1 else ADVANCE.get(t, 8)
    return w


def wrap_page(text, width):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        cand = f"{cur} {w}" if cur else w
        if cur and px(cand) > width:
            lines.append(cur)
            cur = w
        else:
            cur = cand
    lines.append(cur)
    return lines


def wrap(e, en):
    """English as stored: dialogue pages wrapped, quote indent added, banners centred. Other forms unchanged."""
    if form(e) == "banner":
        return " " * max(0, (144 - px(en.strip())) // 8) + en.strip()
    if form(e) == "menu" and not e.get("max_tiles"):
        # each line centred where the JP line was centred (JP pads with leading spaces), never past its right edge;
        # a name insert counts at its longest (character 8 tiles, item NAME_CAP) on both sides, a glyph token
        # ({009F} 。) as one tile
        def tiles(s):
            s = re.sub(r"\{FA[0-9A-F]{2}\}", lambda m: "#" * INSERT_TILES.get(m[0], 0), s)
            return len(TOKEN.sub("", re.sub(r"\{00[0-9A-F]{2}\}", "#", s)))
        jl = e["jp"].split("{nl}")
        el = en.split("{nl}")
        if len(jl) == len(el):
            out = []
            for j, x in zip(jl, el):
                n = len(j) - len(j.lstrip(" "))
                if n and not x.startswith(" "):
                    jw, xw = tiles(j.rstrip(" ")), tiles(x)
                    pad = max(0, min(n + (jw - n - xw + 1) // 2, max(e["tiles"], MSG_BOX.get(e["id"], 0)) - xw))
                    x = " " * pad + x
                out.append(x)
            return "{nl}".join(out)
        return en
    if form(e) not in ("dlg", "epilogue"):
        return en
    # Speech state runs across pages: a page opening with `"` (after any leading control tokens such as {FB00}) starts
    # speech, a page opening with a speaker name line (`Name{nl}"...`) too; continuation pages stay indented.
    # A page `Name{nl}"speech` keeps the name line and wraps the speech (the name counts as one of the 3 lines).
    # When the English has as many pages as the JP, each JP page decides: a page whose text starts with a letter
    # (no 「, no leading space, no name line) is narration and ends the speech.
    speech = False
    out = []
    jp_pages = re.split(r"\{page2?\}", e["jp"])
    en_parts = re.split(r"(\{page2?\})", en)
    narration = [False] * len(jp_pages)
    if len(jp_pages) == (len(en_parts) + 1) // 2:
        for i, p in enumerate(jp_pages):
            t = re.sub(r"^(?:\{[0-9A-F]{4}\})*", "", p)
            narration[i] = bool(t) and t[0] not in "「 " and "{nl}「" not in t
    for k, part in enumerate(en_parts):
        if part in ("{page}", "{page2}"):
            out.append(part)
            continue
        if part.strip() == "":
            out.append(part)
            continue
        lead = re.match(r"(?:\{[0-9A-F]{4}\})*", part)[0]
        body = part[len(lead):]
        head = []
        if "{nl}" in body:
            first, rest = body.split("{nl}", 1)
            if quoted(rest) and not quoted(first) and speaker_line(first):
                head, body = [first.strip()], rest
        if quoted(body):
            speech = True
        elif k // 2 < len(narration) and narration[k // 2]:
            speech = False
        if "{nl}" in body:
            lines = [ln.strip() for ln in body.split("{nl}")]
        else:
            lines = wrap_page(body.strip(), DLG_PX - 4 * speech - (0 if head else px(lead)))
        # choice lines ({F600} = choice cursor) keep their place
        lines = [ln if not speech or quoted(ln) or ln.startswith("{F600}") or ln == "" or indented(ln) else " " + ln
                 for ln in lines]
        out.append(lead + "{nl}".join(head + lines))
    return "".join(out)


def quoted(s):
    """Text opening with `"` once leading control tokens ({wait}, {D320}, {FB00}...) are skipped."""
    return re.sub(r"^(?:\{[0-9A-Za-z]+\})*", "", s.strip()).startswith('"')


def indented(s):
    """A line already indented after its leading control tokens (`{D320} I have no words.`)."""
    return bool(re.match(r"^(?:\{[0-9A-Za-z]+\})+ ", s))


def speaker_line(s):
    """A speaker name line above speech: short, no sentence punctuation (`King of Guld`, `Keukenhof-sensei`)."""
    t = TOKEN.sub("", s).strip()
    return 0 < len(t) <= 20 and not re.search(r"[.!?,\"]", t)


def pages(en):
    return [p.split("{nl}") for p in re.split(r"\{page2?\}", en)]


def width_problems(e, en):
    f = form(e)
    out = []
    if f not in ("name", "battle") and e.get("size", 99) < 5 and not e.get("ptrs") and e["id"] not in REPOINTED:
        words = len(TOKEN.findall(en)) + len(TOKEN.sub("", en))
        if 2 * words > e["size"]:
            out.append(f"{words} words in a {e['size']}-byte slot (too short to relocate: max {e['size'] // 2})")
    if f in ("dlg", "epilogue", "credit", "banner"):
        lim = {"credit": 192, "banner": 144}.get(f, DLG_PX + 4)
        for pg in pages(en):
            for ln in pg:
                if px(ln) > lim:
                    out.append(f"line {px(ln)} px > {lim}: {ln!r}")
            jp_lines = max(len(p) for p in pages(e["jp"]))
            if f == "dlg" and len(pg) > max(3, jp_lines):
                out.append(f"{len(pg)} lines on one page (max 3): add a {{page}}")
        if f == "banner" and "{nl}" in en:
            out.append("banner is one line")
    elif f == "charname":
        if len(en) > 8:
            out.append("name over 8 chars")
    elif f == "menu":
        plain = TOKEN.sub(lambda m: "" if m[0] != "{nl}" else "\n", en)
        lines = plain.split("\n")
        cap = MENU_CAP.get(e["id"]) or e.get("max_tiles") or max(e["tiles"], MSG_BOX.get(e["id"], 0))
        if e.get("max_tiles") or e["id"] in REPOINTED:
            most = e.get("max_lines") or REPOINTED[e["id"]]
            if len(lines) > most:
                out.append(f"{len(lines)} lines > {most}")
        elif len(lines) != len(TOKEN.sub(lambda m: "" if m[0] != "{nl}" else "\n", e["jp"]).split("\n")):
            out.append("line count differs from the JP")
        # a line with a name insert counts it at its longest English width; it may use the whole message box, or
        # as much as the JP line did with 8-tile names
        def widths(s, en_caps):
            def tiles(t):
                return 0 if t not in INSERT_TILES else INSERT_TILES[t] if en_caps else 8
            s = re.sub(r"\{FA[0-9A-F]{2}\}", lambda m: "#" * tiles(m[0]), s)
            return [len(TOKEN.sub("", ln)) for ln in s.split("{nl}")]
        named = [any(t in ln for t in INSERT_TILES) for ln in en.split("{nl}")]
        jp_w = widths(e["jp"], False)
        for i, (ln, w) in enumerate(zip(lines, widths(en, True))):
            if not named[i]:
                if len(ln) > cap:
                    out.append(f"line over {cap} chars: {ln!r}")
                continue
            most = max(MSG_BOX.get(e["id"], 0), jp_w[i] if i < len(jp_w) else 0)
            if w > most:
                out.append(f"line {w} tiles with names at their longest (item {NAME_CAP}, character 8) > {most}: "
                           f"{en.split('{nl}')[i]!r}")
        # {009E} draws a number right-aligned over the blanks before it (status screen: "Attack  {009E}" lost its
        # "k"): keep at least the JP's blanks in front of each one
        gaps = lambda s: [len(m[1]) for m in re.finditer(r"( *)\{009E\}", s)]  # noqa: E731
        for i, (g_en, g_jp) in enumerate(zip(gaps(en), gaps(e["jp"]))):
            if g_en < g_jp:
                out.append(f"value {i + 1} ({{009E}}): {g_en} blanks before it < JP {g_jp} (it overwrites the label)")
    elif f == "battle" and list((ROOT / "rom").glob("*.sfc")):
        try:
            import battle_text
            battle_text.encode(rom(), dict(e, en=en))
        except Exception as x:  # noqa: BLE001 - the encoder's refusal is the message
            out.append(f"battle rect: {x}")
    elif f == "name":
        import insert
        cap = {"enemies": 16, "spells": 8, "tactics": TACTIC_CAP}.get(e["_file"], NAME_CAP)
        if len(TOKEN.sub("", en)) > cap:
            out.append(f"over {cap} chars")
        if e["_file"] == "enemies" and not insert.battle_fits(en):
            out.append("does not split into two rows of 8")
        if e["_file"] == "spells" and not insert.battle_fits(en + " A"):
            out.append("name + rank does not fit two rows of 8")
    return out


def encodable(e, char):
    if form(e) in ("menu", "name", "charname", "battle"):
        return char in BG3_CHARS
    return " " <= char <= "~" and char not in "{}[]"
# ---- end of ADAPTER ----


def kind(char):
    if "぀" <= char <= "ゟ":
        return "hiragana"
    if "゠" <= char <= "ヿ":
        return "katakana"
    if "一" <= char <= "鿿" or char == "々":
        return "kanji"
    return "other"


def has_term(jp, term):
    jp = jp.replace(" / ", "").replace("－", "ー")
    term = term.replace("－", "ー")
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if (a == 0 or kind(jp[a - 1]) != kind(term[0])) and (b == len(jp) or kind(jp[b]) != kind(term[-1])):
            return True
    return False


def glossary():
    rows = []
    if not GLOSSARY.exists():
        return rows
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-: "):
            avoid = [x.strip() for x in cells[4].split("/") if x.strip()] if len(cells) > 4 else []
            rows.append(([x.strip() for x in cells[0].split("/")], [x.strip() for x in cells[1].split("/")], avoid))
    return rows


def problems(entry, en, terms):
    jp = entry["jp"]
    if not en.strip():
        return ["empty English"]
    out = []
    plain = TOKEN.sub("", en)
    if bad := sorted({c for c in plain if not encodable(entry, c)}):
        out.append(f"unencodable characters {bad}")
    if re.search(r"\\u[0-9a-fA-F]{4}", en) or "\t" in en or "\\n" in en:
        out.append("escape sequence or tab in the English")
    free = FREE | ({"{009F}"} if form(entry) == "menu" else set())  # the BG3 full-stop tile: English writes "."
    want = Counter(t for t in TOKEN.findall(jp) if t not in free)
    have = Counter(t for t in TOKEN.findall(en) if t not in free)
    if form(entry) == "name":  # English byte names are plain ASCII (insert.NameTable): a token prints as typed
        if have:
            out.append(f"control codes in a name print as text: {dict(have)}")
    elif want != have and form(entry) not in LAYOUT_FREE:
        out.append(f"control codes differ: JP {dict(want)} EN {dict(have)}")
    if re.search(VARIABLE + r"(st|nd|rd|th)\b", en):
        out.append('ordinal suffix after a variable (write "No. {num}")')
    jp_plain = TOKEN.sub("", jp)
    en_terms = " ".join(TOKEN.sub(" ", en).split()).lower()
    tiny = (form(entry) == "battle" and entry["w"] < 10  # a 7-tile mana label can't hold "Fire Mana"
            or form(entry) == "menu" and (entry.get("tiles", 99) < 6  # 4-tile name labels: "Regi"
                                          or entry.get("max_tiles")))  # 6-tile description box: "Fena-/mun"
    for jps, ens, avoid in terms:
        if not tiny and any(has_term(jp_plain, j) for j in jps) and not any(" ".join(x.split()).lower() in en_terms for x in ens):
            out.append(f"glossary: {jps[0]} -> {ens[0]}")
        out += [f"glossary Avoid: {a}" for a in avoid if re.search(rf"\b{re.escape(a)}\b", en)]
    return out + honorific_problems(entry, jp_plain, en) + width_problems(entry, en)


def honorific_problems(entry, jp, en):
    if entry.get("id") in HONORIFIC_WAIVED:
        return []
    names = {}
    for m in HONORIFIC_RE.finditer(jp):
        if m.group(1) in HONORIFIC_NOT_NAMES or jp[:m.start()].endswith(HONORIFIC_TITLES):
            continue
        names.setdefault(HONORIFICS[m.group(2)], set()).add(m.group(1))
    return [f"honorific: {'/'.join(sorted(n))} + {s} -> '-{s}'"
            for s, n in names.items() if len(re.findall(rf"-{s}", en, re.I)) < len(n)]


def index():
    result = {}
    for _, _, entries in docs():
        for e in entries:
            key = entry_key(e)
            if key in result:
                raise ValueError(f"duplicate batch key {key!r}")
            result[key] = e
    return result


def read_tsv(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def existing():
    return sorted(TL.glob("b[0-9][0-9][0-9].tsv"))


def split(size):
    index()
    TL.mkdir(parents=True, exist_ok=True)
    (ROOT / "build").mkdir(exist_ok=True)
    taken = {r[0] for p in existing() for r in read_tsv(p)}
    n = max((int(p.stem[1:]) for p in existing()), default=0)
    groups = {}
    for _, _, entries in docs():
        for e in entries:
            if needs_english(e) and entry_key(e) not in taken:
                groups.setdefault((e["_file"], group_of(e)), []).append(e)
    batches, cur, chars, curfile = [], [], 0, None
    for (fname, _), group in groups.items():
        c = sum(len(TOKEN.sub("", e["jp"])) for e in group)
        small = c < 400 and chars + c <= size * 1.15  # keep a short room with its neighbour
        if cur and (chars + c > size and not small or len(cur) + len(group) > MAX_ENTRIES):
            batches.append(cur)
            cur, chars = [], 0
        cur += group
        chars += c
    if cur:
        batches.append(cur)
    terms = glossary()
    for batch in batches:
        n += 1
        name = f"b{n:03d}"
        path = TL / f"{name}.tsv"
        if path.exists():
            sys.exit(f"{path} already exists")
        rows = [f"{entry_key(e)}\t{e.get('speaker', '')}\t{form(e)}\t{limit_label(e)}\t{e['jp']}" for e in batch]
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        jps = " ".join(TOKEN.sub("", e["jp"]) for e in batch)
        used = sorted({(j, ens[0]) for jpl, ens, _ in terms for j in jpl if has_term(jps, j)})
        (ROOT / f"build/terms_{name}.txt").write_text("".join(f"{j}\t{x}\n" for j, x in used)
                                                      or "(no glossary terms in this batch)\n", encoding="utf-8", newline="\n")
    print(f"{len(batches)} new batches in {TL}, {len(taken)} ids already batched")


def check_batch(batch, entries, terms):
    want = [r[0] for r in read_tsv(TL / f"{batch}.tsv")]
    rows = [(r[0], "\t".join(r[1:])) for r in read_tsv(TL / f"{batch}.out.tsv")]
    bad = []
    if [r[0] for r in rows] != want:
        got = [r[0] for r in rows]
        dup = sorted(i for i, c in Counter(got).items() if c > 1)
        bad.append(f"ids differ: missing {sorted(set(want) - set(got))[:8]} extra {sorted(set(got) - set(want))[:8]} "
                   f"duplicate {dup[:8]} (order must match too)")
    out = {}
    for eid, en in rows:
        if eid in entries:
            en = wrap(entries[eid], en)
            out[eid] = en
            bad += [f"{eid}: {p}" for p in problems(entries[eid], en, terms)]
    return bad, out


def merge(new, overwrite):
    if not overwrite:
        for _, _, entries in docs():
            for e in entries:
                if entry_key(e) in new and e.get("en") and e["en"] != new[entry_key(e)]:
                    sys.exit(f"{e['id']} would lose {e['en']!r}: pass --overwrite if that is meant")
    changed = 0
    for path, doc, entries in docs():
        touched = False
        for e in entries:
            e.pop("_file"), e.pop("_kind")
            if entry_key(e) in new and e.get("en") != new[entry_key(e)]:
                e["en"] = new[entry_key(e)]
                touched = True
                changed += 1
        if touched:
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"merged: {changed} entries changed")


def keep_jp():
    """script/keep_jp.txt: `id  reason` per line (# comments): entries allowed to ship without English. An entry
    listed without a reason, unknown, or translated is an error (returned with an empty or stale reason)."""
    path = ROOT / "script" / "keep_jp.txt"
    out = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                eid, _, why = line.strip().partition(" ")
                out[eid] = why.strip()
    return out


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "split":
        return split(int(args[args.index("--size") + 1]) if "--size" in args else 3500)
    if cmd == "fit":
        f = args[args.index("--form") + 1] if "--form" in args else "dlg"
        e = {"_file": "r000" if f == "dlg" else "credits", "_kind": "block", "id": "x", "jp": ""}
        for pg in pages(wrap(e, args[0])):
            print("\n".join(f"{px(ln):4d} {ln}" for ln in pg) + "\n----")
        return 0
    overwrite = "--overwrite" in args
    names = [a for a in args if a != "--overwrite"]
    entries, terms = index(), glossary()
    if cmd == "check" and not names:
        bad = [f"{i}: {p}" for i, e in entries.items() if e.get("en") for p in problems(e, e["en"], terms)]
        keep = keep_jp()
        bad += [f"{i}: untranslated (translate it, or list it in script/keep_jp.txt with a reason)"
                for i, e in entries.items() if e.get("jp", "").strip() and not e.get("en") and i not in keep]
        bad += [f"{i}: script/keep_jp.txt: no reason, unknown id, or translated" for i, why in keep.items()
                if not why or i not in entries or entries[i].get("en")]
        print(f"{len(entries)} entries, {sum(bool(e.get('en')) for e in entries.values())} translated, {len(bad)} problems")
        print("\n".join(bad[:200]))
        return 1 if bad else 0
    if cmd == "show":
        _, rows = check_batch(names[0], entries, terms)
        for eid, en in rows.items():
            print(f"== {eid}\n" + "\n".join(f"{px(ln):4d}|{ln}" for pg in pages(en) for ln in pg + ["-"]))
        return 0
    if cmd not in ("check", "merge") or not names:
        sys.exit(__doc__)
    failed = 0
    for batch in names:
        bad, rows = check_batch(batch, entries, terms)
        failed += bool(bad)
        print(f"{batch}: " + ("OK" if not bad else f"{len(bad)} problems"))
        for line in bad:
            print("  " + line)
        if cmd == "merge" and not bad:
            merge(rows, overwrite)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
