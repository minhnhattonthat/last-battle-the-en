"""re_blocks.py: walk the compressed-block pointer tables at $1A:8000 (file 0xD0000) and decompress every block.

Pointers are 24-bit linear addresses (01:FDDF converts them to LoROM): file = 0xD0000 + (ptr - 0x1A8000).
Prints one line per pointer: table entry, file offset, compressed size, decompressed size, and whether the result
looks like script (16-bit words with font codes and FE00/FF00) or something else."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lz import decompress  # noqa: E402

ROM = Path(__file__).resolve().parents[1] / "rom" / "Last Battle, The (Japan).sfc"


def lin2off(p):
    return 0xD0000 + (p - 0x1A8000)


def main():
    rom = ROM.read_bytes()
    first = int.from_bytes(rom[0xD0000:0xD0003], "little")
    n = (lin2off(first) - 0xD0000) // 3
    print("top table entries:", n)
    for i in range(n):
        p = int.from_bytes(rom[0xD0000 + 3 * i:0xD0003 + 3 * i], "little")
        off = lin2off(p)
        try:
            data, size = decompress(rom, off)
            words = [int.from_bytes(data[j:j + 2], "little") for j in range(0, len(data) - 1, 2)]
            kana = sum(1 for w in words if 0x334 <= w < 0x3F0)
            nl = sum(1 for w in words if w in (0xFE00, 0xFF00, 0xFF02))
            print(f"{i:3d} ptr={p:06X} off={off:06X} csize={size:5d} dsize={len(data):6d} kana={kana:5d} breaks={nl:4d}")
        except Exception as e:  # noqa: BLE001
            print(f"{i:3d} ptr={p:06X} off={off:06X} not a block ({e.__class__.__name__})")


if __name__ == "__main__":
    main()
