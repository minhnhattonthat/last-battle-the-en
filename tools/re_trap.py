"""Recon: free-space trap ROM. Fills each candidate run of $00 (docs/re/compression.md) with $FF, writes
work/trap.sfc, and lists 16-bit operands in the ROM that point into a candidate (absolute addresses in the same
LoROM bank, and 24-bit long addresses), so a run can be checked statically as well as by touring.

    python -X utf8 tools/re_trap.py [--min 1024] [--xrefs]
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / "rom" / "Last Battle, The (Japan).sfc"


def zero_runs(rom, min_len):
    out, i = [], 0
    while i < len(rom):
        if rom[i]:
            i += 1
            continue
        j = i
        while j < len(rom) and not rom[j]:
            j += 1
        if j - i >= min_len:
            out.append((i, j))
        i = j
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=1024)
    ap.add_argument("--xrefs", action="store_true")
    a = ap.parse_args()
    rom = bytearray(ROM.read_bytes())
    runs = zero_runs(rom, a.min)
    for s, e in runs:
        bank, lo, hi = s // 0x8000, 0x8000 + s % 0x8000, 0x8000 + (e - 1) % 0x8000
        print(f"{s:06X}-{e:06X} {e - s:6d} bytes  ${bank:02X}:{lo:04X}-${(e - 1) // 0x8000:02X}:{hi:04X}")
        if a.xrefs:
            # long addresses (bank, lo..hi) anywhere; JSR/JMP/LDA abs operands inside the same bank
            for p in range(len(rom) - 3):
                v = int.from_bytes(rom[p:p + 3], "little")
                b, ad = v >> 16, v & 0xFFFF
                if b in (bank, bank | 0x80) and ad >= 0x8000 and s <= bank * 0x8000 + ad - 0x8000 < e:
                    print(f"    long ref at {p:06X}: {v:06X}")
    out = bytearray(rom)
    for s, e in runs:
        out[s:e] = b"\xff" * (e - s)
    (ROOT / "work").mkdir(exist_ok=True)
    (ROOT / "work" / "trap.sfc").write_bytes(out)
    print(f"{len(runs)} runs trapped -> work/trap.sfc")


if __name__ == "__main__":
    main()
