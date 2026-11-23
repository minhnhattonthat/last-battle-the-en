"""Text-coverage runs: warp to each room and run every script entry of its block (tools/debug/textcover.lua), logging
which strings the game read, for $SKILL/scripts/textcover.py.

    python -X utf8 tools/debug/textcover_run.py OUTDIR [--rom build/lastbattle_en.sfc] [--rooms 1,2,5-9] [--jobs 3]
    python -X utf8 $SKILL/scripts/textcover.py OUTDIR build/strings.tsv --waive docs/text_unshown.tsv \
        --mask 0xFFFFFFFFFFFF

Room id N (1-based, $0D24) loads room block N-1 (table 0xD0081). Entries: script_dis.walk_room (e0, e1, search spots,
talk tables, step triggers). A run that leaves the room (a door or BA warp), sticks, or never starts is restarted
after the entry it stopped on, so one bad script costs only itself. Each attempt is OUTDIR/r<id>_<n>/ (log.txt).
Keep build/strings.tsv of the same build with the runs (keys follow block placement)."""
import argparse
import concurrent.futures as cf
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import script_dis  # noqa: E402
from skill import SKILL  # noqa: E402
from strings_tsv import BLOCK_KEY  # noqa: E402

ORIG = ROOT / "rom" / "Last Battle, The (Japan).sfc"


def rom_ranges(strings):
    """CPU read ranges (both mirrors) of every 32 KB bank holding a ROM string key."""
    banks = set()
    for line in strings.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        k = int(line.split("\t")[1], 16)
        if not k & BLOCK_KEY:
            banks.add(k >> 15)
    out = []
    for b in sorted(banks):
        for cpu in ({b, b | 0x80} if b < 0x40 else {b | 0x80}):
            out.append(f"{cpu:02X}8000-{cpu:02X}FFFF")
    return ",".join(out)


# Story-variant blocks (docs/re/debug.md §Story variants): script_dis room index -> (room id, pokes). $EC = k loads
# block 28+k (index 308+k) in room B34B[k-1]; flag $026F loads blocks 39-42 (index 319-322) in rooms 1, $1A, $88, $F8.
VARIANTS = {308 + k: (r, f"EC={k:02X}") for k, r in enumerate((1, 0x15, 0x78, 0x89, 0xB9, 0x107, 0xDB, 0x10C, 0x110,
                                                                0xF8), 1)}
VARIANTS.update({319 + i: (r, "026F=01") for i, r in enumerate((1, 0x1A, 0x88, 0xF8))})


def room_entries(orig, idx):
    _off, d = script_dis.room_block(orig, idx)
    return list(dict.fromkeys(e for e in script_dis.walk_room(d, idx)[3] if 18 <= e < len(d)))


def parse_rooms(spec):
    out = []
    for part in spec.split(","):
        lo, _, hi = part.partition("-")
        out += range(int(lo), int(hi or lo) + 1)
    return out


def emu_run(a, d, rid, pokes, ranges, extra, frames):
    d.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), a.rom, "--out", str(d),
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"),
           "--script", str(ROOT / "tools" / "debug" / "textcover.lua"),
           "--frames", str(frames), "--timeout", "900",
           "--var", f"ROOM={rid}", "--var", f"X={a.x}", "--var", f"Y={a.y}", "--var", "GOD=1", "--var", "WIN=1",
           "--var", f"POKES='{pokes}'", "--var", f"RANGES='{ranges}'"] + extra
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""


def run_room(a, idx, entries, ranges):
    rid, pokes = VARIANTS.get(idx, (idx + 1, "-"))
    todo, n, notes = list(entries), 0, []
    while todo and n < len(entries) + 2:
        d = Path(a.out) / f"r{idx + 1:03d}_{n}"
        log = emu_run(a, d, rid, pokes, ranges, ["--var", "RUNS='" + ",".join(f"{e:04X}" for e in todo) + "'"],
                      a.frames)
        if "ALLDONE" in log:
            return idx + 1, notes + [f"{n}: all done"]
        m = re.search(r"^(LEFT|STUCK|NOSTART) ([0-9A-F]{4})", log, re.M)
        ended = re.findall(r"^END ([0-9A-F]{4})", log, re.M)
        if m and m.group(1) == "NOSTART" and not ended:
            # the field loop never takes an injected script here (an event holds it): run each entry in place of
            # the room's entry script instead, one boot each, A mashed for a fixed time
            for e in todo:
                emu_run(a, Path(a.out) / f"r{idx + 1:03d}_e{e:04X}", rid, pokes, ranges,
                        ["--var", f"RUN=0x{e:04X}", "--mash", "12"], 5500)
            return idx + 1, notes + [f"{n}: NOSTART, {len(todo)} entries run as the entry script"]
        if m:
            bad = int(m.group(2), 16)
            notes.append(f"{n}: {m.group(1)} {bad:04X}")
            todo = todo[todo.index(bad) + 1:] if bad in todo else todo[len(ended) + 1:]
        else:
            notes.append(f"{n}: no end marker (frames out?) after {len(ended)} ends")
            todo = todo[len(ended) + 1:]
        n += 1
    return idx + 1, notes


def room_done(out, rid):
    """True when an earlier run of room rid in out finished (ALLDONE, or the per-entry fallback ran)."""
    if any(out.glob(f"r{rid:03d}_e*")):
        return True
    return any("ALLDONE" in p.read_text(encoding="utf-8", errors="replace")
               for p in out.glob(f"r{rid:03d}_*/log.txt"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--rom", default=str(ROOT / "build" / "lastbattle_en.sfc"))
    ap.add_argument("--strings", default=str(ROOT / "build" / "strings.tsv"))
    ap.add_argument("--rooms", default=f"1-{script_dis.ROOM_COUNT + len(script_dis.EXTRA_ROOMS)}",
                    help="script_dis room index + 1 (310-323: the story-variant blocks, warped with their pokes)")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--frames", type=int, default=40000)
    ap.add_argument("--x", default="10")
    ap.add_argument("--y", default="8")
    ap.add_argument("--skip-done", action="store_true",
                    help="skip rooms whose earlier run in OUT ended with ALLDONE or ran entries one by one (same build)")
    a = ap.parse_args()
    orig = ORIG.read_bytes()
    ranges = rom_ranges(Path(a.strings))
    jobs = [(n - 1, room_entries(orig, n - 1)) for n in parse_rooms(a.rooms)
            if (ROOT / "script" / f"r{n - 1:03d}.json").exists()]  # rooms with no text have no script file
    if a.skip_done:
        jobs = [j for j in jobs if not room_done(Path(a.out), j[0] + 1)]
        print(f"{len(jobs)} rooms to run", flush=True)
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for rid, notes in ex.map(lambda j: run_room(a, j[0], j[1], ranges), jobs):
            print(f"room {rid}: {'; '.join(notes)}", flush=True)


if __name__ == "__main__":
    main()
