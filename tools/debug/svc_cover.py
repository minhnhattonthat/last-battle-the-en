"""Text-coverage probes for field actions the room runs never take (session 27): chests, field magic, seal items,
the magic healer's Combine/Review/Split screens and the "file erased" message. Logs reads with textcover.lua.

    python -X utf8 tools/debug/svc_cover.py OUTDIR chest|magic|seal|synth|erased [--rom R] [--strings S] [--only 0,2]
        [--jobs 2]

chest   the chest op from warp.lua OPS: A0 flag item (found / nothing inside / no room / party no room), A1 money
magic   field casts with Kurt's spell slot 0 poked (Restore at HP 1, MP 0, Escape, Teleport, Awaken, Tornado)
seal    Seal Tome with no spell / one spell; Seal Stone ($F5) holding Restore / Fireball at $1CF1
synth   E4 07 00 (top21): Combine / Review / Split with 3 or 12 known spells and 9,999,999 Sol
review  Review with one known spell of each of the 22 types (descriptions and effect labels)
bmagic  battle Cmd > Cast with 12 known spells (types 0-11, 10-21), walking the list (spell info column)
bparty  battles with all four members ($1DD4-$1DD7): victory windows, Run, battle item list and item use
erased  title LOAD forced to fail (tools/debug/load_fail.lua, needs work/saves/base_file1.srm)
Defaults: the frozen coverage build work/qa/cover_build (rom.sfc + strings.tsv). Report over work/qa/cover.
Spell types (slot byte 0, low 5 bits) are the distinct spells in order of first appearance in spells.json.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "tools" / "debug"), str(ROOT / "tools")]
import textcover_run  # noqa: E402
from skill import SKILL  # noqa: E402

P = "0x4D 10 6 "
ITEM = "60 -;6 a;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 a;90 -;6 a;120 -"
MAGIC = "60 -;6 a;40 -;6 right;40 -;6 right;40 -;6 a;90 -;6 a;120 -"
TAIL = ";6 a;120 -;6 a;120 -;6 a;150 -;6 a;150 -;6 a;150 -;6 a;150 -;6 a;150 -"
TEXT_A = ";300 -;6 a;60 -;6 a;60 -;6 a;60 -;6 a"
HPLOW, MP99, MP0 = "@1909:0001", "@190D:0063", "@190D:0000"
MONEY = ["@1DD1:967F", "@1DD3:0098"]


def slot(a, t, n):
    """A known spell slot at a: type t, name n (02 n 41 = rank A)."""
    return [f"@{a:04X}:03{0x80 | t:02X}", f"@{a + 2:04X}:0303", f"@{a + 4:04X}:{n:02X}02",
            f"@{a + 6:04X}:0041", f"@{a + 8:04X}:0000", f"@{a + 10:04X}:0000", f"@{a + 12:04X}:5012"]


def kurt(spells):
    pk = []
    for j in range(12):
        a = 0x1927 + 14 * j
        pk += slot(a, *spells[j]) if j < len(spells) else [f"@{a:04X}:0000"]
    return pk


def type_names():
    """Name number (1-based, spells.json order) of each of the 22 spell types: the t-th distinct spell."""
    import json
    names = {}
    for n, e in enumerate(json.loads((ROOT / "script" / "spells.json").read_text(encoding="utf-8"))["entries"], 1):
        names.setdefault(e["en"], n)
    return list(names.values())[:22]


def specs(kind):
    if kind == "chest":
        full = []
        for base in (0x19CF, 0x1AB3, 0x1B97, 0x1C7B):  # every record's 16 item slots
            full += [f"@{base + i:04X}:4342" for i in range(0, 16, 2)]
        party = ["@003E:0004", "@0600:0100", "@0602:0302"]
        k = P + "100 -" + TEXT_A
        return [k + "|00A042|-", k + "|00A1640000|-", k + "|00A000|-", k + "|80A000|-",
                k + "|00A042|" + ",".join(full[:8]), k + "|00A042|" + ",".join(full + party)]
    if kind == "magic":
        out = [P + MAGIC + TAIL + "|-|" + ",".join(kurt([sp]) + extra)
               for sp, extra in [((7, 11), [HPLOW, MP99]), ((7, 11), [HPLOW, MP0]), ((13, 20), [MP99]),
                                 ((15, 22), [MP99]), ((16, 23), [MP99]), ((4, 6), [MP99])]]
        out.append(P + MAGIC + ";6 a;120 -;6 a;120 -;" + "6 down;30 -;" * 18 + "6 a;120 -;6 a;120 -;6 a;120 -|-|"
                   + ",".join(kurt([(15, 22)]) + [MP99]))
        return out
    if kind == "seal":
        return [P + ITEM + TAIL + "|-|" + ",".join(kurt([]) + ["@19CF:00FA"]),
                P + ITEM + TAIL + "|-|" + ",".join(kurt([(0, 1)]) + ["@19CF:00FA", MP99]),
                P + ITEM + TAIL + "|-|" + ",".join(slot(0x1CF1, 7, 11) + ["@19CF:00F5", HPLOW]),
                P + ITEM + TAIL + "|-|" + ",".join(slot(0x1CF1, 0, 1) + ["@19CF:00F5"])]
    if kind == "synth":  # the menu opens with its question: the first A picks, so the cursor moves first
        walk = (";6 a;90 -;6 a;90 -;6 a;120 -;6 a;120 -;" + "6 right;30 -;6 down;30 -;6 a;90 -;" * 6 +
                "6 a;90 -;" * 10 + "60 -")
        known = [(j, j + 1) for j in range(12)]
        out = [P + "120 -" + ";6 down;30 -" * opt + walk + "|07E400|" + ",".join(kurt(known[:k]) + MONEY + [MP99])
               for opt in (1, 2, 3) for k in (3, 12)]
        # Split a Tornado / Icestorm / Quake: "has become {FA4D} again" names the wind / water / earth mana
        out += [P + "120 -;6 down;30 -;6 down;30 -;6 down;30 -" + walk + "|07E400|" +
                ",".join(kurt([sp]) + MONEY + [MP99]) for sp in ((4, 6), (5, 7), (9, 16))]
        return out
    if kind == "review":  # Review one known spell per type: its description and effect labels on the screen
        keys = P + "120 -;6 down;30 -;6 down;30 -;6 a;90 -;6 a;90 -;6 a;120 -;6 a;120 -;400 -"
        return [keys + "|07E400|" + ",".join(kurt([(t, n)]) + MONEY + [MP99]) for t, n in enumerate(type_names())]
    if kind == "bmagic":  # battle: Cmd > Cast > Kurt, walk the spell list (info column per spell type)
        walk = "6 down;40 -;" * 6 + "6 right;40 -;" + "6 up;40 -;" * 6 + "6 left;40 -;"
        keys = "0x00 40 30 1100 -;6 a;150 -;6 right;40 -;6 a;120 -;6 a;120 -;6 a;120 -;" + walk * 2 + "60 -"
        tn = type_names()
        return [keys + "|-|" + ",".join(["god", "@1DDF:0053"] + kurt([(t, tn[t]) for t in ts]) + [MP99])
                for ts in (range(0, 12), range(10, 22))]
    if kind == "bparty":  # battles with all four members: the battle party is the ids at $1DD4-$1DD7 (30:9CEA),
        # not $3E/$0600; members 2-4 get HP so they stand. Victory windows, Run, item list walk + use.
        party = ["@1DD4:0201", "@1DD6:0403", "@003E:0004", "@0600:0100", "@0602:0302"]
        for rec in (0x19E4, 0x1AC8, 0x1BAC):
            party += [f"@{rec + 9:04X}:0050", f"@{rec + 0xB:04X}:0050", f"@{rec + 0xD:04X}:0020", f"@{rec + 0xF:04X}:0020"]
        items = [0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A, 0x4B, 0x4C, 0x4D, 0x4E, 0x56, 0x57, 0x59]
        inv = [f"@{0x19CF + i:04X}:{items[i + 1]:02X}{items[i]:02X}" for i in range(0, 16, 2)]
        b = "0x00 40 30 1100 -;"
        mash = "6 a;120 -;" * 20
        walk = "6 down;40 -;" * 8 + "6 right;40 -;" + "6 up;40 -;" * 8
        use = "6 a;150 -;6 right;40 -;6 right;40 -;6 a;120 -;6 a;120 -;"
        out = [b + mash + "60 -|-|" + ",".join(["god", "win", "@1DDF:0053"] + party),
               b + ("6 right;40 -;6 right;40 -;6 a;300 -;" * 4) + "60 -|-|" + ",".join(["god", "@1DDF:0053"] + party),
               b + use + walk + "6 a;120 -;6 a;120 -;6 a;200 -|-|" + ",".join(["god", "@1DDF:0053"] + party + inv)]
        for k in range(1, 6):  # use item k (down k) on Kurt, HP and MP low: the use messages
            out.append(b + use + "6 down;40 -;" * k + "6 a;120 -;6 a;120 -;6 a;200 -|-|" +
                       ",".join(["@1DDF:0053", HPLOW, MP0] + party + inv))
        return out
    raise SystemExit(kind)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("kind", choices=["chest", "magic", "seal", "synth", "review", "bmagic", "bparty", "erased"])
    ap.add_argument("--rom", default=str(ROOT / "work" / "qa" / "cover_build" / "rom.sfc"))
    ap.add_argument("--strings", default=str(ROOT / "work" / "qa" / "cover_build" / "strings.tsv"))
    ap.add_argument("--only", default="", help="comma-separated spec indexes")
    ap.add_argument("--jobs", default="2")
    a = ap.parse_args()
    ranges = textcover_run.rom_ranges(Path(a.strings))
    lua = ["--script", str(ROOT / "tools" / "debug" / "textcover.lua"), "--var", f"RANGES='{ranges}'"]
    if a.kind == "erased":
        subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), a.rom, "--out", a.out,
                        "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--var", "SCENE='load_file1'",
                        "--sav", str(ROOT / "work" / "saves" / "base_file1.srm"), "--frames", "2000",
                        "--shot-every", "30", "--script", str(ROOT / "tools" / "debug" / "load_fail.lua"), *lua])
        return
    sp = specs(a.kind)
    if a.only:
        sp = [sp[int(i)] for i in a.only.split(",")]
    frames = {"chest": 3000, "synth": 4400, "bmagic": 5200, "bparty": 5600}.get(a.kind, 3400)
    subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "debug" / "probe.py"), a.out, *sp,
                    "--rom", a.rom, "--frames", str(frames), "--jobs", a.jobs, *lua])


if __name__ == "__main__":
    main()
