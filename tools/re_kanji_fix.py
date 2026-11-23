"""re_kanji_fix.py: apply eye-checked corrections to the aligner output and write tbl/font_jp.tsv (code, char).

    python -X utf8 tools/re_kanji_fix.py [work/kanji_align.tsv]
Corrections come from proof sheets (tools/re_tbl_sheet.py). Checks that $0384-$07AD is strictly increasing in
JIS X 0208 order (a wrong reading usually breaks it) and that no char repeats."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORDERED_END = 0x7AE
FIX = {  # code: char read off the proof sheets
    0x42E: "改", 0x444: "株", 0x445: "冠", 0x465: "機", 0x493: "教", 0x494: "橋", 0x4B5: "敬", 0x4E1: "五",
    0x4E8: "候", 0x4F5: "校", 0x520: "祭", 0x522: "裁", 0x532: "賛", 0x580: "襲", 0x5C0: "深", 0x5CD: "図",
    0x5D0: "数", 0x5ED: "跡", 0x67C: "殿", 0x6B9: "熱", 0x6BA: "年", 0x6C1: "破", 0x6CF: "畑", 0x6D8: "板",
    0x6EE: "姫", 0x6FB: "怖", 0x700: "舞", 0x721: "補", 0x728: "放", 0x729: "方", 0x72A: "法", 0x73D: "満",
    0x73E: "味", 0x78F: "領", 0x799: "鈴", 0x7A3: "錬", 0x7A5: "労", 0x7A9: "録", 0x7AA: "論", 0x7AB: "和",
    0x7AC: "話", 0x7AD: "腕",
}
# $07AE-$07D0: extra kanji outside JIS order (staff names in the credits), read off work/re_tail.png.
TAIL = "裔居孝岡本郎哲綾弘雅之崎剛浩喜充菅桂荘晃麻伊寿景塚克沢坪井健泰博尾隆企"


def jis(ch):
    b = ch.encode("euc_jp")
    return (b[0] & 0x7F) << 8 | (b[1] & 0x7F)


def main():
    src = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "work" / "kanji_align.tsv")
    m = {int(c, 16): ch for c, ch, *_ in (ln.split("\t") for ln in src.read_text(encoding="utf-8").splitlines())}
    m.update(FIX)
    for i, ch in enumerate(TAIL):
        m[ORDERED_END + i] = ch
    assert max(m) == 0x7D0, hex(max(m))
    bad = 0
    for c in range(0x385, ORDERED_END):
        if jis(m[c]) <= jis(m[c - 1]):
            print(f"order break at {c:04X}: {m[c - 1]}({jis(m[c - 1]):04X}) -> {m[c]}({jis(m[c]):04X})")
            bad += 1
    seen = {}
    for c, ch in sorted(m.items()):
        if ch in seen and c < ORDERED_END:  # the tail repeats 本 ($0736 = $07B2), as the glyph bytes show
            print(f"duplicate {ch}: {seen[ch]:04X} and {c:04X}")
            bad += 1
        seen[ch] = c
    out = ROOT / "tbl" / "font_jp.tsv"
    out.write_text("".join(f"{c:04X}\t{m[c]}\n" for c in sorted(m)), encoding="utf-8")
    print(out, len(m), "glyphs;", bad, "problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
