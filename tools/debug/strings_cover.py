"""Text coverage for room-script strings no room run reached: most sit in branches behind story flags. Room text is
inline in the VM stream (character words up to FF00), so the probe warps to the room that loads the block and runs
the VM straight at each unshown string (textcover_run.run_room with the string offsets as entries): the line is drawn
in its real box with the build's wrap, outside its story context.

    python -X utf8 $SKILL/scripts/textcover.py work/qa/cover work/qa/cover_build/strings.tsv \
        --waive docs/text_unshown.tsv --mask 0xFFFFFFFFFFFF > work/qa/cover_report.txt
    python -X utf8 tools/debug/strings_cover.py work/qa/cover/str work/qa/cover_report.txt [--rooms 2,5] [--jobs 3]
    python -X utf8 tools/debug/strings_cover.py work/qa/cover/str work/qa/cover_report.txt --top

--top: shop/inn/healer strings (top-table blocks 14-28): one run each, the service op E4 (14 + lo) in room 0x4D
with tools/debug/topstr.lua pointing every script slot of the block at the string.

The offset run is the string key's low 16 bits (offset of its first byte in the $7F block, this build), so run it on
the coverage build (work/qa/cover_build) only. Output OUT/r<id>_<n>/ like textcover_run; report over work/qa/cover."""
import argparse
import concurrent.futures as cf
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "tools" / "debug")]
import textcover_run  # noqa: E402

COVER = ROOT / "work" / "qa" / "cover_build"


def missing_rooms(report):
    """{script room index: sorted string offsets} for every NEVER SHOWN r### string in a textcover.py report."""
    rooms = {}
    for m in re.finditer(r"^NEVER SHOWN\s+r(\d{3})_[0-9A-F]+\s+([0-9A-F]+)", report, re.M):
        rooms.setdefault(int(m.group(1)), set()).add(int(m.group(2), 16) & 0xFFFF)
    return {k: sorted(v) for k, v in sorted(rooms.items())}


def missing_top(report):
    """[(id, op bytes, key)] for every NEVER SHOWN top<N>_ string (shops, inns, healers: op E4 lo with top block
    14 + lo) and common_ string (op E5 00: the common block)."""
    out = []
    for m in re.finditer(r"^NEVER SHOWN\s+((top(\d+)|common)_[0-9A-F]+)\s+([0-9A-F]+)", report, re.M):
        op = f"{int(m.group(3)) - 14:02X}E400" if m.group(3) else "00E5"
        out.append((m.group(1), op, int(m.group(4), 16)))
    return out


def patched(log):
    return log.exists() and "TOPSTR" in log.read_text(encoding="utf-8", errors="replace")


def run_top(a, sid, op, key, ranges):
    """The op that loads the block, in room 0x4D, with tools/debug/topstr.lua pointing its scripts at the string."""
    out = Path(a.out) / "top" / sid
    log = out / "p00_0x4D_10_6" / "log.txt"
    if patched(log):
        return sid, "done before"
    cmd = [sys.executable, "-X", "utf8", str(ROOT / "tools" / "debug" / "probe.py"), str(out),
           f"0x4D 10 6 30 -;6 a;60 -;6 a;60 -;6 a;60 -;6 a;90 -|{op}|-", "--rom", a.rom,
           "--frames", "3000", "--jobs", "1", "--script", str(ROOT / "tools" / "debug" / "textcover.lua"),
           "--script", str(ROOT / "tools" / "debug" / "topstr.lua"), "--var", f"RANGES='{ranges}'",
           "--var", f"TOPSTR='{key & 0xFFFF:04X}'", "--var", f"STREAM='{(key >> 16) & 0xFFFFFF:06X}'"]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return sid, "patched" if patched(log) else "NOT PATCHED"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("report")
    ap.add_argument("--rom", default=str(COVER / "rom.sfc"))
    ap.add_argument("--strings", default=str(COVER / "strings.tsv"))
    ap.add_argument("--rooms", help="room ids (script index + 1), e.g. 2,5-9")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--frames", type=int, default=40000)
    ap.add_argument("--x", default="10")
    ap.add_argument("--y", default="8")
    ap.add_argument("--top", action="store_true", help="the top-table service strings instead of the rooms")
    a = ap.parse_args()
    if a.top:
        ranges = textcover_run.rom_ranges(Path(a.strings))
        todo = missing_top(Path(a.report).read_text(encoding="utf-8"))
        print(f"{len(todo)} service strings", flush=True)
        with cf.ThreadPoolExecutor(a.jobs) as ex:
            for sid, note in ex.map(lambda t: run_top(a, *t, ranges), todo):
                print(f"{sid}: {note}", flush=True)
        return
    rooms = missing_rooms(Path(a.report).read_text(encoding="utf-8"))
    if a.rooms:
        keep = set(textcover_run.parse_rooms(a.rooms))
        rooms = {k: v for k, v in rooms.items() if k + 1 in keep}
    ranges = textcover_run.rom_ranges(Path(a.strings))
    print(f"{len(rooms)} rooms, {sum(map(len, rooms.values()))} strings", flush=True)
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for rid, notes in ex.map(lambda j: textcover_run.run_room(a, j[0], j[1], ranges), rooms.items()):
            print(f"room {rid}: {'; '.join(notes)}", flush=True)


if __name__ == "__main__":
    main()
