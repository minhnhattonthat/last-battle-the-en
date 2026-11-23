"""compare_runs.py: compare two run_scenes.py output dirs scene by scene (final.png, pixel for pixel).

    python -X utf8 tools/debug/compare_runs.py work/qa/scenes work/qa/scenes_new [--tol 0.0] [--sheet DIR]

Prints one line per scene whose final frame differs (fraction of differing pixels) and a count. --sheet writes a
side-by-side pair per differing scene (via the skill's sheet.py --compare) into DIR. Exit 1 if any scene differs
by more than --tol or is missing from either run. Use it for builds that must not change the screen (identity,
relocation) or to list exactly which scenes an edit touched."""
import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))


def diff_fraction(a, b):
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    if ia.size != ib.size:
        return 1.0
    bbox_diff = ImageChops.difference(ia, ib).convert("L").point(lambda v: 255 if v else 0)
    hist = bbox_diff.histogram()
    return hist[255] / (ia.size[0] * ia.size[1])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--tol", type=float, default=0.0)
    ap.add_argument("--sheet")
    args = ap.parse_args()
    a, b = Path(args.a), Path(args.b)
    names = sorted({p.parent.name for p in a.glob("*/final.png")} | {p.parent.name for p in b.glob("*/final.png")})
    bad = 0
    for n in names:
        fa, fb = a / n / "final.png", b / n / "final.png"
        if not (fa.is_file() and fb.is_file()):
            print(f"{n}: missing in {'A' if not fa.is_file() else 'B'}")
            bad += 1
            continue
        d = diff_fraction(fa, fb)
        if d > args.tol:
            bad += 1
            print(f"{n}: {d:.4f} of pixels differ")
            if args.sheet:
                from skill import SKILL
                out = Path(args.sheet)
                out.mkdir(parents=True, exist_ok=True)
                subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), str(fa),
                                "--compare", str(fb), "--out", str(out / f"{n}.png")], check=False)
    print(f"{len(names)} scenes, {bad} differ")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
