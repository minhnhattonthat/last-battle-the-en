"""Text-coverage probes for names: poke the item ids (or spells) the last coverage report never showed into Kurt's
record and open the field list, logging reads with tools/debug/textcover.lua.

    python -X utf8 tools/debug/names_cover.py OUTDIR items|spells [--report work/qa/cover_report.txt]
        [--rom work/qa/cover_build/rom.sfc] [--strings work/qa/cover_build/strings.tsv]

Items: 16 slots at $19CF (record $1900 + $CF), 16 ids per run, item menu in room 0x4D (all 135 shown, session 24).
Spells: Kurt's 12 spell slots at $1927 + 14i (01:EEFD: byte 0 bit 7 = known, name `02 n 41` at +4, n = position in
spells.json), magic menu ("Who will cast?" list)."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "tools" / "debug"), str(ROOT / "tools")]
import textcover_run  # noqa: E402

ITEM_KEYS = "60 -;6 a;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 a;90 -;6 a;120 -"
MAGIC_KEYS = "60 -;6 a;40 -;6 right;40 -;6 right;40 -;6 a;90 -;6 a;120 -"


def specs(kind, miss):
    out = []
    if kind in ("items", "itemdesc"):
        if kind == "items":
            ids = [int(m[5:], 16) for m in miss if m.startswith("item_")]
            keys = ITEM_KEYS
        else:  # every item: the box left of the list describes the item under the cursor (bg3 descriptions)
            doc = json.loads((ROOT / "script" / "items.json").read_text(encoding="utf-8"))
            ids = [int(e["id"][5:], 16) for e in doc["entries"]]
            keys = ITEM_KEYS + ";6 a;120 -;" + "6 right;40 -;6 left;40 -;6 down;40 -;" * 8 + "60 -"
        for g in range(0, len(ids), 16):
            s = ids[g:g + 16] + [0] * (16 - len(ids[g:g + 16]))
            pk = ",".join(f"@{0x19CF + i:04X}:{s[i + 1]:02X}{s[i]:02X}" for i in range(0, 16, 2))
            out.append(f"0x4D 10 6 {keys}|-|{pk}")
    elif kind == "examine":  # item > Examine prints the long description (b04 text) and returns to the field; the
        # menus keep their cursors, so the second cycle only reopens them; later cycles drift: 2 items per run
        doc = json.loads((ROOT / "script" / "items.json").read_text(encoding="utf-8"))
        ids = [int(e["id"][5:], 16) for e in doc["entries"]] + [0]
        close = "6 a;150 -;6 a;100 -;6 b;60 -;6 b;60 -;6 b;60 -"
        keys = (ITEM_KEYS.replace("6 a;90 -;6 a;120 -", "6 a;90 -;6 right;40 -;6 a;120 -;6 a;120 -") +
                f";{close};6 a;60 -;6 a;60 -;6 a;80 -;6 a;80 -;6 right;30 -;{close}")
        for g in range(0, len(ids) - 1, 2):
            out.append(f"0x4D 10 6 {keys}|-|@19CF:{ids[g + 1]:02X}{ids[g]:02X}")
    elif kind == "use":  # item > Use on Kurt: recovery / stat-rise / seal messages (b04 B864-BB72); one item a run,
        # Kurt's HP and MP poked low first so recovery has something to do
        ids = list(range(0x42, 0x50)) + list(range(0x56, 0x5C)) + [0xF5, 0xFA]
        keys = ITEM_KEYS + ";6 a;120 -;6 a;120 -;6 a;150 -;6 a;150 -;6 a;150 -;6 a;150 -;6 a;150 -"
        for i in ids:
            out.append(f"0x4D 10 6 {keys}|-|@19CF:00{i:02X},@1909:0001,@190D:0001")
    elif kind == "sealdesc":  # seal items $F5-$FF hold a spell slot at $1CF1 + 14 * (id - $F5) (01:F413); with
        # the flag set their description is the spell type's short name ($04:A7A5 table, 23 entries)
        keys = ITEM_KEYS + ";6 a;120 -;" + "6 right;40 -;6 left;40 -;6 down;40 -;" * 6 + "60 -"
        for g in range(0, 23, 11):
            s = list(range(0xF5, 0x100)) + [0] * 5
            pk = [f"@{0x19CF + i:04X}:{s[i + 1]:02X}{s[i]:02X}" for i in range(0, 16, 2)]
            for k, t in enumerate(range(g, min(g + 11, 23))):
                a = 0x1CF1 + 14 * k
                pk += [f"@{a:04X}:03{0x80 | t:02X}", f"@{a + 2:04X}:0303", f"@{a + 4:04X}:{t + 1:02X}02",
                       f"@{a + 6:04X}:0041"]
            out.append(f"0x4D 10 6 {keys}|-|" + ",".join(pk))
    elif kind == "menus":  # field-menu paths with a 4-member party ($3E = 4, $0600 list 0-3: the HP/MP box shows
        # all four), gear and herbs in Kurt's slots and 12 known spells (names 11-22, types 10-21: Teleport among
        # them); five cursor walks under each of the 8 menu icons
        pk = ["@003E:0004", "@0600:0100", "@0602:0302", "@19CF:0201", "@19D1:4342", "@19D3:0A09"]
        for j in range(12):
            a, n, t = 0x1927 + 14 * j, j + 11, j + 10
            pk += [f"@{a:04X}:03{0x80 | t:02X}", f"@{a + 2:04X}:0303", f"@{a + 4:04X}:{n:02X}02",
                   f"@{a + 6:04X}:0041", f"@{a + 8:04X}:0000", f"@{a + 10:04X}:0000", f"@{a + 12:04X}:5012"]
        walks = ["6 a;90 -;6 a;90 -;6 a;90 -;6 a;90 -;6 b;60 -;6 b;60 -",
                 "6 down;40 -;6 a;90 -;6 a;90 -;6 a;90 -;6 a;90 -",
                 "6 right;40 -;6 a;90 -;6 down;40 -;6 a;90 -;6 a;90 -;6 a;90 -",
                 "6 right;40 -;6 right;40 -;6 a;90 -;6 a;90 -;6 down;40 -;6 a;90 -;6 a;90 -",
                 "6 right;40 -;6 right;40 -;6 right;40 -;6 a;90 -;6 a;90 -;6 a;90 -;6 a;90 -"]
        for i in range(8):
            for w in walks:
                out.append("0x4D 10 6 60 -;6 a;40 -;" + "6 right;40 -;" * i + f"6 a;90 -;{w}|-|" + ",".join(pk))
    elif kind == "battles":  # enemy names: one forced battle per encounter group id ($1DDF, 0x00-0xBF), idle in
        # god mode; the battle start draws each enemy's name (30:AD08)
        for g in range(0xC0):
            out.append(f"0x00 40 30 1100 -|-|god,@1DDF:00{g:02X}")
    else:
        doc = json.loads((ROOT / "script" / "spells.json").read_text(encoding="utf-8"))
        pos = {e["id"]: n for n, e in enumerate(doc["entries"], 1)}
        ns = [pos[m] for m in miss if m in pos]
        keys = MAGIC_KEYS
        if kind == "spelldesc":  # the box beside the list describes the spell under the cursor by its type: the
            ns = list(range(1, 23))  # flag byte's low 5 bits, 22 types (jump table 01:F6BA); poked as type n-1

            keys += ";6 a;120 -;" + "6 right;40 -;6 left;40 -;6 down;40 -;" * 6 + "60 -"
        for g in range(0, len(ns), 12):
            pk = []
            for j, n in enumerate(ns[g:g + 12]):
                a = 0x1927 + 14 * j  # slot: known flag $80, 3 bytes, 8-byte name (02 n 41 = rank A), 2 bytes
                t = n - 1 if kind == "spelldesc" else 0
                pk += [f"@{a:04X}:03{0x80 | t:02X}", f"@{a + 2:04X}:0303", f"@{a + 4:04X}:{n:02X}02", f"@{a + 6:04X}:0041",
                       f"@{a + 8:04X}:0000", f"@{a + 10:04X}:0000", f"@{a + 12:04X}:5012"]
            out.append(f"0x4D 10 6 {keys}|-|" + ",".join(pk))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("kind", choices=["items", "itemdesc", "examine", "use", "sealdesc", "spells", "spelldesc",
                                     "battles", "menus"])
    ap.add_argument("--jobs", default="3")
    ap.add_argument("--frames", type=int, default=3200)
    ap.add_argument("--report", default=str(ROOT / "work" / "qa" / "cover_report.txt"))
    ap.add_argument("--rom", default=str(ROOT / "work" / "qa" / "cover_build" / "rom.sfc"))
    ap.add_argument("--strings", default=str(ROOT / "work" / "qa" / "cover_build" / "strings.tsv"))
    a = ap.parse_args()
    miss = [line.split()[2] for line in open(a.report, encoding="utf-8") if line.startswith("NEVER SHOWN")]
    sp = specs(a.kind, miss)
    if not sp:
        print("nothing missing")
        return
    ranges = textcover_run.rom_ranges(Path(a.strings))
    # Windows caps a command line at 32K: long poke lists go in chunks, each to its own OUT/c<k> (one chunk: OUT)
    n = 8 if len(" ".join(sp)) > 20000 else len(sp)
    for k in range(0, len(sp), n):
        out = a.out if n == len(sp) else str(Path(a.out) / f"c{k // n}")
        subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "debug" / "probe.py"), out, *sp[k:k + n],
                        "--rom", a.rom, "--frames", str(a.frames), "--jobs", a.jobs,
                        "--script", str(ROOT / "tools" / "debug" / "textcover.lua"), "--var", f"RANGES='{ranges}'"])


if __name__ == "__main__":
    main()
