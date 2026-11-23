"""Text-coverage probes for names: poke the item ids (or spells) the last coverage report never showed into Kurt's
record and open the field list, logging reads with tools/debug/textcover.lua.

    python -X utf8 tools/debug/names_cover.py OUTDIR items|spells [--report work/qa/cover_report.txt]
        [--rom work/qa/cover_build/rom.sfc] [--strings work/qa/cover_build/strings.tsv]

Items: 16 slots at $19CF (record $1900 + $CF), 16 ids per run, item menu in room 0x4D (all 135 shown, session 24).
Spells: Kurt's spell fields at $192A + 8i (`02 n 41`, n = position in spells.json), magic menu. Not working yet: the
list shows only one entry, so the spell count is kept elsewhere (docs/status.md)."""
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
    if kind == "items":
        ids = [int(m[5:], 16) for m in miss if m.startswith("item_")]
        for g in range(0, len(ids), 16):
            s = ids[g:g + 16] + [0] * (16 - len(ids[g:g + 16]))
            pk = ",".join(f"@{0x19CF + i:04X}:{s[i + 1]:02X}{s[i]:02X}" for i in range(0, 16, 2))
            out.append(f"0x4D 10 6 {ITEM_KEYS}|-|{pk}")
    else:
        doc = json.loads((ROOT / "script" / "spells.json").read_text(encoding="utf-8"))
        pos = {e["id"]: n for n, e in enumerate(doc["entries"], 1)}
        ns = [pos[m] for m in miss if m in pos]
        for g in range(0, len(ns), 7):
            pk = []
            for j, n in enumerate(ns[g:g + 7]):
                a = 0x192A + 8 * j
                pk += [f"@{a:04X}:{n:02X}02", f"@{a + 2:04X}:0041"]
            out.append(f"0x4D 10 6 {MAGIC_KEYS}|-|" + ",".join(pk))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("kind", choices=["items", "spells"])
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
                    "--rom", a.rom, "--frames", "3200", "--jobs", "3",
                    "--script", str(ROOT / "tools" / "debug" / "textcover.lua"), "--var", f"RANGES='{ranges}'"])


if __name__ == "__main__":
    main()
