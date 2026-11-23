"""re_battle_text.py: list runs of BG3 tile words with the battle palette bits ($20xx/$21xx) in banks $28-$33 that
hold >= 3 kana tiles (battle messages, battle status/equip labels, mana and spell info screens; docs/re/battle.md).
Both byte alignments; tiles >= $100 print as {xxx} (kanji / two-row tiles), $93 as a space.

    python -X utf8 tools/re_battle_text.py [OUT.txt]"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from textcodec import bg3_tiles  # noqa: E402

BANKS = range(0x28, 0x34)
MIN_KANA = 3


def runs(rom):
    kana = bg3_tiles(rom)
    out = []
    for bank in BANKS:
        base = bank * 0x8000
        for al in (0, 1):
            cur, st, i = [], None, base + al
            while i < base + 0x7FFF:
                w = rom[i] | rom[i + 1] << 8
                t = w & 0x3FF
                if (w >> 8) & 0xFE == 0x20 and (t in kana or t >= 0x100 or t == 0x93):
                    st = i if st is None else st
                    cur.append(w)
                else:
                    if sum((x & 0x3FF) in kana for x in cur) >= MIN_KANA:
                        out.append((st, cur))
                    cur, st = [], None
                i += 2
    text = []
    for st, ws in sorted(out):
        s = "".join(kana.get(w & 0x3FF, " " if (w & 0x3FF) == 0x93 else "{%x}" % (w & 0x3FF)) for w in ws)
        text.append((st, len(ws), s))
    return text


def main():
    rom = (ROOT / "rom" / "Last Battle, The (Japan).sfc").read_bytes()
    rs = runs(rom)
    lines = [f"{st:06X} {n:3d} {s}" for st, n, s in rs]
    lines.append(f"{len(rs)} runs, {sum(n for _, n, _ in rs)} tile words")
    txt = "\n".join(lines) + "\n"
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(txt, encoding="utf-8")
    else:
        sys.stdout.write(txt)


if __name__ == "__main__":
    main()
