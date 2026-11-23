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
    ap.add_argument("kind", choices=["items", "itemdesc", "sealdesc", "spells", "spelldesc"])
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
    subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "debug" / "probe.py"), a.out, *sp,
                    "--rom", a.rom, "--frames", str(a.frames), "--jobs", "3",
                    "--script", str(ROOT / "tools" / "debug" / "textcover.lua"), "--var", f"RANGES='{ranges}'"])


if __name__ == "__main__":
    main()
