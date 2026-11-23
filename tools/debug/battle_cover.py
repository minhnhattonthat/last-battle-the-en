"""Which battle text rects (script/battle.json) does the game read along some battle routes?

    python -X utf8 tools/debug/battle_cover.py OUTDIR [--rom build/marker.sfc] [--frames 6000] [--routes FILE]
                                               [--only a,b]

Routes: tools/debug/battle_routes.tsv (name, room, x, y, keys, pokes). Each route runs through probe.py with
tools/lua/rect_reads.lua; the logs give, per id, the first frame and route it was read in, so the shot of that
frame shows the window. Writes OUTDIR/cover.tsv (id, geom, route, frame, jp) and prints the ids never read.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def rect_var(entries):
    items = ",".join(f'{{0x{e["file"]},{e["size"]},"{e["id"]}"}}' for e in entries)
    return f"RECTS={{{items}}}"


def load_routes(path):
    routes = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        assert len(cols) in (6, 7), f"{path}: 6 or 7 columns expected: {line!r}"
        routes.append(cols + ["-"] * (7 - len(cols)))
    return routes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--rom", default=str(ROOT / "build" / "marker.sfc"))
    ap.add_argument("--frames", type=int, default=6000)
    ap.add_argument("--routes", default=str(ROOT / "tools" / "debug" / "battle_routes.tsv"))
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    entries = json.loads((ROOT / "script" / "battle.json").read_text(encoding="utf-8"))["entries"]
    routes = load_routes(a.routes)
    if a.only:
        keep = set(a.only.split(","))
        routes = [r for r in routes if r[0] in keep]
    out = Path(a.out)
    specs = [f"{room} {x} {y} {keys}|{ops}|{pokes}" for _, room, x, y, keys, pokes, ops in routes]
    cmd = [sys.executable, "-X", "utf8", str(ROOT / "tools" / "debug" / "probe.py"), str(out), *specs,
           "--rom", a.rom, "--frames", str(a.frames), "--jobs", str(a.jobs),
           "--script", str(ROOT / "tools" / "lua" / "rect_reads.lua"), "--var", rect_var(entries)]
    subprocess.run(cmd, check=True)
    first = {}
    for i, (name, room, x, y, *_) in enumerate(routes):
        log = out / f"p{i:02d}_{room}_{x}_{y}" / "log.txt"
        if not log.exists():
            print(f"{name}: no log")
            continue
        for m in re.finditer(r"^RECT (\S+) f(\d+)", log.read_text(encoding="utf-8", errors="replace"), re.M):
            rid, f = m.group(1), int(m.group(2))
            if rid not in first:
                first[rid] = (name, f, i)
    rows = ["id\tgeom\troute\tframe\tjp"]
    for e in entries:
        name, f, _ = first.get(e["id"], ("", "", 0))
        rows.append(f'{e["id"]}\t{e["geom"]}\t{name}\t{f}\t{e["jp"]}')
    (out / "cover.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    missing = [e["id"] for e in entries if e["id"] not in first]
    print(f"read {len(first)}/{len(entries)}; never read ({len(missing)}): {' '.join(missing)}")


if __name__ == "__main__":
    main()
