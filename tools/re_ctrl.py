"""re_ctrl.py: list the text engine's control codes (high byte >= $80) and whether each handler reads more script.

The engine (01:B79F) reads 16-bit words through [$10]; a word >= $8000 goes to 01:BA96, which looks its high byte
up in the table at 01:BAB5 and jumps through 01:BAED. A handler that touches [$10] or $10 (the script pointer) is
flagged, with its first lines of disassembly, so the argument count can be read off by eye."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Last Battle, The (Japan).sfc"
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402


def main():
    rom = ROM.read_bytes()
    codes = []
    o = 0xBAB5
    while o < 0xBAED:
        codes.append(rom[o])
        o += 1
    handlers = [int.from_bytes(rom[0xBAED + 2 * i:0xBAED + 2 * i + 2], "little") for i in range(len(codes))]
    verbose = "-v" in sys.argv
    for c, h in zip(codes, handlers):
        out = subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "dis65816.py"), str(ROM),
                              "01%04X" % h, "80"], capture_output=True, text=True).stdout.splitlines()
        body = []
        for line in out:
            body.append(line[:70])
            if re.search(r"\bRT[SL]\b", line):
                break
        touches = [l for l in body if re.search(r"\[\$10\]|\$10\b", l)]
        jsrs = sorted({m.group(1) for l in body for m in [re.search(r"JSR \$(\w{4})", l)] if m})
        print(f"{c:02X}xx -> 01:{h:04X}  lines={len(body):3d}  script-ptr={len(touches)}  jsr={','.join(jsrs)}")
        if verbose and touches:
            for l in touches:
                print("      ", l)


if __name__ == "__main__":
    main()
