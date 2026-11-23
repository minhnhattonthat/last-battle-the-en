"""Warp to every scene in tools/debug/scenes.tsv (or the ones named) from a cold boot, in parallel.

    python -X utf8 tools/debug/run_scenes.py [ROM] [--only a,b] [--jobs 3] [--out work/qa/scenes] [--states]
                                             [--hold 300] [--var NAME=LUA]..

Each scene gets work/qa/scenes/<name>/ with shots every 30 frames after READY, final.png, log.txt, and a
1x contact sheet sheet.png of the frames after READY. --states also saves work/states/<name>.mss at the end
(regenerate the whole library after engine, font or graphics changes). Exit 1 if any scene failed: emulator
error, no READY line in its log (the warp never reached the field), or its final frame is flat.
"""
import argparse
import concurrent.futures as cf
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

DEFAULT_ROM = ROOT / "build" / "lastbattle_en.sfc"
ORIG_ROM = ROOT / "rom" / "Last Battle, The (Japan).sfc"
SCENES = ROOT / "tools" / "debug" / "scenes.tsv"


def load_scenes(path=SCENES):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) != 9:
            raise SystemExit(f"{path.name}: {len(cols)} columns, want 9: {line!r}")
        rows.append(dict(zip("name room x y dir pokes run keys notes".split(), cols)))
    return rows


def key_frames(keys):
    if keys == "-":
        return 0
    return sum(int(step.split()[0]) for step in keys.split(";"))


def run(scene, rom, out, hold, states, extra):
    d = out / scene["name"]
    frames = 2300 + key_frames(scene["keys"]) + hold
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(d),
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--var", f"SCENE='{scene['name']}'",
           "--frames", str(frames), "--shot-every", "30", "--timeout", "900"]
    if states:
        cmd += ["--state-out", str(ROOT / "work" / "states" / f"{scene['name']}.mss")]
    for v in extra["vars"]:
        cmd += ["--var", v]
    for s in extra["scripts"]:
        cmd += ["--script", str(Path(s).resolve())]
    d.mkdir(parents=True, exist_ok=True)
    with open(d.parent / f"{scene['name']}.emu.log", "w", encoding="utf-8") as f:
        rc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT).returncode
    log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
    m = re.search(r"READY f(\d+)", log)
    problem = None
    if rc != 0:
        problem = f"emu.py exit {rc}"
    elif not m:
        problem = "never READY"
    if m:
        subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), str(d),
                        "--from", m.group(1), "--changed", "0.01", "--max", "16"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return scene["name"], problem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", nargs="?", default=None)
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "scenes"))
    ap.add_argument("--hold", type=int, default=300)
    ap.add_argument("--states", action="store_true")
    ap.add_argument("--var", action="append", default=[])
    ap.add_argument("--script", action="append", default=[], help="extra Lua probe(s) after warp.lua")
    a = ap.parse_args()
    extra = {"vars": a.var, "scripts": a.script}
    rom = Path(a.rom) if a.rom else (DEFAULT_ROM if DEFAULT_ROM.exists() else ORIG_ROM)
    scenes = load_scenes()
    if a.only:
        want = set(a.only.split(","))
        missing = want - {s["name"] for s in scenes}
        if missing:
            raise SystemExit(f"unknown scenes: {sorted(missing)}")
        scenes = [s for s in scenes if s["name"] in want]
    out = Path(a.out)
    bad = []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for name, problem in ex.map(lambda s: run(s, rom, out, a.hold, a.states, extra), scenes):
            print(f"{'FAIL' if problem else 'ok  '} {name}" + (f": {problem}" if problem else ""), flush=True)
            if problem:
                bad.append(name)
    print(f"{len(scenes) - len(bad)}/{len(scenes)} scenes reached ({rom.name})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
