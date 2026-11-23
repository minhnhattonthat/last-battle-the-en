"""Ad-hoc warps in parallel, no scenes.tsv row needed (finding positions, ops, flags).

    python -X utf8 tools/debug/probe.py OUTDIR "ROOM X Y [KEYS [OPS [POKES]]]" ... [--frames 2600] [--script x.lua]
                                        [--var NAME=LUA].. [--rom ROM]

Each spec becomes OUTDIR/p<i>_<room>_<x>_<y>/ (shots every 30 frames, final.png); prints the READY line of each and
writes OUTDIR/finals.png, the final frames side by side. KEYS/OPS/POKES as in scenes.tsv ('-' = none).
"""
import argparse
import concurrent.futures as cf
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("specs", nargs="+")
    ap.add_argument("--frames", type=int, default=2600)
    ap.add_argument("--script", action="append", default=[])
    ap.add_argument("--var", action="append", default=[])
    ap.add_argument("--rom", default=str(ROOT / "rom" / "Last Battle, The (Japan).sfc"))
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--mash", type=int, default=0, help="press A every N frames once the keys are done")
    a = ap.parse_args()
    out = Path(a.out)

    def one(i, spec):
        f = spec.split(" ", 3)
        room, x, y = f[0], f[1], f[2]
        rest = f[3].split("|") if len(f) > 3 else []
        d = out / f"p{i:02d}_{room}_{x}_{y}"
        cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), a.rom, "--out", str(d),
               "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--frames", str(a.frames),
               "--shot-every", "30", "--timeout", "900",
               "--var", f"ROOM={room}", "--var", f"X={x}", "--var", f"Y={y}"]
        for name, val in zip(("KEYS", "OPS", "POKES"), rest):
            if val.strip() != "-":
                cmd += ["--var", f"{name}='{val.strip()}'"]
        for s in a.script:
            cmd += ["--script", str(Path(s).resolve())]
        for v in a.var:
            cmd += ["--var", v]
        if a.mash:
            cmd += ["--mash", str(a.mash)]
        d.mkdir(parents=True, exist_ok=True)
        rc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT).returncode
        log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
        ready = [l for l in log.splitlines() if l.startswith("READY")]
        return d, rc, ready[0] if ready else "never READY"

    with cf.ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda t: one(*t), enumerate(a.specs)))
    for d, rc, ready in res:
        print(f"{d.name}: exit {rc}, {ready}")
    finals = [str(d / "final.png") for d, _, _ in res if (d / "final.png").exists()]
    if finals:
        subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), *finals,
                        "--cols", "3", "--out", str(out / "finals.png")], stdout=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
