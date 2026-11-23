"""check.py: the repo's one-command check (tests + text lint). The pre-commit hook runs it; exit code gates the commit.

Tests that need the ROM skip themselves when rom/ is missing, so a fresh clone still passes the structural tests."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    r = subprocess.run([sys.executable, "-X", "utf8", "-m", "pytest", "-q", str(ROOT / "tests")], cwd=ROOT)
    if r.returncode not in (0,):
        sys.exit(r.returncode)
    r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "batches.py"), "check"], cwd=ROOT)
    if r.returncode:
        sys.exit(r.returncode)
    lint = ROOT / "tools" / "lint.py"
    if lint.is_file():
        r = subprocess.run([sys.executable, "-X", "utf8", str(lint)], cwd=ROOT)
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
