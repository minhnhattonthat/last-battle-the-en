"""List the random-encounter tables: zone key -> (weight, group id) lists (30:EBD9 reads $2A:A080).

    python -X utf8 tools/re_encounters.py [--groups]   (--groups: only the sorted distinct group ids)
Table at $2A:A080: (zone key word, pointer word) pairs, FFFF end. Each list at $2A:ptr: (weight byte, group word)
entries, FF end; 30:EC0F picks the first entry whose running weight sum reaches a random byte. The group goes to
$7E1DDF, which the field loop (00:979E) turns into a battle.
"""
import sys
from pathlib import Path

ROM = Path(__file__).resolve().parents[1] / "rom" / "Last Battle, The (Japan).sfc"


def off(bank, addr):
    return (bank << 15) | (addr & 0x7FFF)


def tables(d):
    t = off(0x2A, 0xA080)
    out = []
    while True:
        key = d[t] | d[t + 1] << 8
        if key == 0xFFFF:
            break
        ptr = d[t + 2] | d[t + 3] << 8
        p = off(0x2A, ptr)
        ents = []
        while d[p] != 0xFF:
            ents.append((d[p], d[p + 1] | d[p + 2] << 8))
            p += 3
        out.append((key, ptr, ents))
        t += 4
    return out


def main():
    d = ROM.read_bytes()
    tabs = tables(d)
    if "--groups" in sys.argv:
        print(" ".join(f"{g:02X}" for g in sorted({g for _, _, e in tabs for _, g in e})))
        return
    for key, ptr, ents in tabs:
        print(f"zone {key:04X} @{ptr:04X}: " + " ".join(f"{w}:{g:02X}" for w, g in ents))


if __name__ == "__main__":
    main()
