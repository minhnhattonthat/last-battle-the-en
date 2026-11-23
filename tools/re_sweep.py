"""Graphics-text static sweep (docs/re/graphics.md): render the whole ROM and every non-script LZ block as tile
sheets for reading by eye. Nothing is skipped; every region rendered is printed with its sheet.

    python -X utf8 tools/re_sweep.py [--out work/sweep] [--fmt snes2] [--chunk 20000] [--cols 64]

Sheet raw_XXXXXX.png covers file offsets XXXXXX .. +chunk; tile (row r, col c) is at offset
XXXXXX + (r * cols + c) * tile_bytes (16 for snes2, 32 for snes4, 8 for 1bpp). A grey bar is drawn every
0x1000 bytes on the left edge to help locate rows.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from lz import decompress  # noqa: E402
from skill import SKILL  # noqa: E402

TILE = {"snes2": 16, "snes4": 32, "1bpp": 8, "snes8": 64}
GRAPHICS_TOP = [2, 3, 4, 5, 6, 8]  # top-table entries that are not script (docs/re/compression.md)


def render(src, dst, fmt, at, length, cols):
    subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "tiles.py"), "render", str(src),
                    str(dst), "--fmt", fmt, "--at", f"{at:X}", "--len", f"{length:X}", "--cols", str(cols),
                    "--zoom", "1"], check=True, capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="work/sweep")
    ap.add_argument("--fmt", default="snes2", choices=sorted(TILE))
    ap.add_argument("--chunk", default="20000")
    ap.add_argument("--cols", type=int, default=64)
    a = ap.parse_args()
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    rom_path = ROOT / "rom" / "Last Battle, The (Japan).sfc"
    rom = rom_path.read_bytes()
    chunk = int(a.chunk, 16)
    for at in range(0, len(rom), chunk):
        dst = out / f"raw_{at:06X}_{a.fmt}.png"
        render(rom_path, dst, a.fmt, at, min(chunk, len(rom) - at), a.cols)
        print(f"{dst.name}: file {at:06X}-{at + chunk:06X}")
    for i in GRAPHICS_TOP:
        p = int.from_bytes(rom[0xD0000 + 3 * i:0xD0003 + 3 * i], "little")
        off = 0xD0000 + (p - 0x1A8000)
        data, _ = decompress(rom, off)
        src = out / f"top{i}.bin"
        src.write_bytes(data)
        for fmt in ("snes2", "snes4", "1bpp"):
            dst = out / f"top{i}_{fmt}.png"
            render(src, dst, fmt, 0, len(data), 16)
            print(f"{dst.name}: top entry {i} (LZ at {off:06X}, {len(data)} bytes)")


if __name__ == "__main__":
    main()
