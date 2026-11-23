"""Readable 1x review sheets for the visual-QA gate.

The tour's sheet.png tiles are 128x112 (too small to read text). For each scene named in a qa_gate chunk file
this writes work/qa/review/<scene>/r.png (r_2.png ...): full frames at 1x from READY on, near-duplicates dropped.

    python -X utf8 tools/debug/review_sheets.py work/qa/chunks/chunk_X_000.txt [--tour work/qa/tour] [--changed 0.02]
Prints one line per scene: scene, pages.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chunk")
    ap.add_argument("--tour", default=str(ROOT / "work" / "qa" / "tour"))
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "review"))
    ap.add_argument("--changed", default="0.02")
    ap.add_argument("--cols", default="4")
    ap.add_argument("--max", default="16")
    a = ap.parse_args()
    scenes = []
    for line in Path(a.chunk).read_text(encoding="utf-8").splitlines():
        if line.strip():
            s = line.split("\t")[0].split("/")[0]
            if s not in scenes:
                scenes.append(s)
    for s in scenes:
        d = Path(a.tour) / s
        log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
        m = re.search(r"READY f(\d+)", log)
        out = Path(a.out) / s
        for old in out.glob("r*.png"):
            old.unlink()
        out.mkdir(parents=True, exist_ok=True)
        cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), str(d), "--changed", a.changed,
               "--div", "1", "--cols", a.cols, "--max", a.max, "--out", str(out / "r.png")]
        if m:
            cmd += ["--from", m.group(1)]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(s, len(list(out.glob("r*.png"))), "" if m else "(no READY)")


if __name__ == "__main__":
    main()
