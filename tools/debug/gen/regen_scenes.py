"""Rewrite tools/debug/scenes.tsv: the core_rows.py rows, then the existing place_*/svc_* rows (from gen_rows.py,
which needs work/e4_all.txt; run it and paste its output only when those change). Run from the repo root:

    python -X utf8 tools/debug/gen/regen_scenes.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
p = ROOT / "tools" / "debug" / "scenes.tsv"
lines = p.read_text(encoding="utf-8").splitlines()
core = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "debug" / "gen" / "core_rows.py")],
                      capture_output=True, text=True, encoding="utf-8", check=True).stdout.splitlines()
kept = [l for l in lines[1:] if l.split("\t")[0].startswith(("place_", "svc_"))]
out = [lines[0]] + core + kept
names = [l.split("\t")[0] for l in out[1:]]
assert len(names) == len(set(names)), "duplicate scene names"
for l in out[1:]:
    assert len(l.split("\t")) == 9, l
p.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print(len(out) - 1, "scenes")
